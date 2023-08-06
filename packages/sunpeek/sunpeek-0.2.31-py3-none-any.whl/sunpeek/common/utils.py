import enum
import logging
import os
import pathlib
import sys
import dotenv
import sqlalchemy.orm
import sqlalchemy.event
from pydantic import BaseModel
from logging.config import dictConfig

from sunpeek.common.unit_uncertainty import to_s

try:
    import uvicorn
    api_modules_available = True
except ModuleNotFoundError:
    # API dependecies are not installed, log only to standard output, no file.
    api_modules_available = False

dotenv.load_dotenv()

ROOT_DIR = os.path.abspath(pathlib.Path(__file__).parent.parent)
log_dir = os.path.join(ROOT_DIR, 'logs')
log_fname = os.path.join(log_dir, 'server.log')

API_LOCAL_BASE_URL = "http://127.0.0.1:8000/"
API_TOKEN = "harvestIT"


async def handle_api_exceptions(caller: str, error_message: str, exception):
    print(f"[handle_api_exceptions] /!\\ An exception ocurred in {caller}. Preparing API and LOG entries...")

    err_type, err_obj, traceback = sys.exc_info()

    # details_dict = {"error_message": error_message, "exception_info": exception.}


class MissingEnvVar(Exception):
    def __init__(self, key):
        super().__init__("Value not found. This information should be stored in env variable " +
                         key + ". use: os.environ['" + key + "'] = <values>")


class LogConfig(BaseModel):
    """
    Logging configuration to be set for the server.

    Notes
    -----
    Modified code snipped originally by "Yash Nag" taken from:
    https://stackoverflow.com/questions/63510041/adding-python-logging-to-fastapi-endpoints-hosted-on-docker-doesnt-display-api

    """

    # LOGGER_NAME: str = "sp_logger"
    FILE_LOG_FORMAT: str = "|%(asctime)s| [%(levelname)s -> %(module)s] : %(message)s"
    STD_OUT_LOG_FORMAT: str = "%(levelprefix)s |%(asctime)s| %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Create log directory if it does not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Logging config
    version = 1
    disable_existing_loggers = False

    if api_modules_available:
        formatters = {
            "std_out": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": STD_OUT_LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "file_out": {
                "format": FILE_LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        }
    else:
        formatters = {
            "std_out": {
                "fmt": STD_OUT_LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        }

    handlers = {
        "default": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }}

    loggers = {"sp_logger": {"handlers": ["default"], "level": LOG_LEVEL},}
    if api_modules_available:
        handlers["file"] = \
            {
            "formatter": "file_out",
            "class": "logging.FileHandler",
            "level": "WARNING",
            "filename": log_fname
            }
        loggers = {"sp_logger": {"handlers": ["default", "file"], "level": LOG_LEVEL},}


def get_env(name):
    try:
        value = os.environ[name]
    except KeyError:
        raise MissingEnvVar(name)
    return value


def get_db_conection_string():
    db_type = os.environ.get('HIT_DB_TYPE', 'postgresql')
    host = os.environ.get('HIT_DB_HOST', 'localhost:5432')
    user = os.environ.get('HIT_DB_USER')
    pw = os.environ.get('HIT_DB_PW')
    db_name = os.environ.get('HIT_DB_NAME', 'harvestit')
    dialects = {'postgresql': 'postgresql+psycopg2'}

    db_str = '{}://'.format(dialects[db_type])
    if user is not None:
        db_str = db_str + user
    if pw is not None:
        db_str = db_str + ':{}@'.format(pw)
    db_str = db_str + '{}/{}'.format(host.strip('/'), db_name)
    return db_str


def to_rd(*args):
    """Converts numeric inputs to pd.Series with pint dtype W/m².
    Useful to return radiation converter results.
    """
    out = *(None if elem is None else to_s(elem, unit_str='W m**-2') for elem in args),
    out = out[0] if len(out) == 1 else out
    return out


try:
    db_engine = sqlalchemy.create_engine(get_db_conection_string(), pool_pre_ping=True)
    S = sqlalchemy.orm.sessionmaker(db_engine)
except ModuleNotFoundError:
    db_engine = None
    S = None


# @sqlalchemy.event.listens_for(db_engine, "connect")
# def connect(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute(f"SET TIME ZONE utc;")
#     cursor.close()


# logger
dictConfig(LogConfig().dict())
sp_logger = logging.getLogger("sp_logger")


class VerifyValidateMode(str, enum.Enum):
    validate = 'validate'
    verify = 'verify'

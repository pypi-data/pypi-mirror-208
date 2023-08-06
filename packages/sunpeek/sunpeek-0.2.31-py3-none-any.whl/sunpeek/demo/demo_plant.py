import json
from datetime import datetime
from sqlalchemy.orm import Session

from sunpeek.common import config_parser, data_uploader
from sunpeek.common.data_uploader import DatetimeTemplates
from sunpeek.db_utils import crud
import sunpeek.components as cmp
import sunpeek.demo


def requires_demo_data(func):
    if not sunpeek.demo.DEMO_DATA_AVAILABLE:
        raise ModuleNotFoundError(
            "This function requires optional dependency sunpeek-demo. Install it with `pip install sunpeek[demo]`")
    return func


@requires_demo_data
def create_demoplant(session: Session, name: str = None):
    with open(sunpeek.demo.DEMO_CONFIG_PATH, 'r') as f:
        conf = json.load(f)

    # Plant name must be unique in database => create unique
    unique_plant_name = f'demoplant_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    name = unique_plant_name if (name is None) else name
    conf['plant']['name'] = name

    config_parser.make_and_store_plant(conf, session)
    return crud.get_plants(session, plant_name=conf['plant']['name'])


@requires_demo_data
def add_demo_data(plant: cmp.Plant, session: Session = None):
    files = [sunpeek.demo.DEMO_DATA_PATH_1MONTH]
    timezone = 'UTC'
    datetime_template = DatetimeTemplates.year_month_day

    if session is not None:
        up = data_uploader.DataUploader_db(plant=plant,
                                           timezone=timezone,
                                           datetime_template=datetime_template,
                                           session=session)
        up.do_upload(files=files)   # includes virtual sensor calculation
    else:
        # includes virtual sensor calculation
        plant.use_csv(csv_files=files,
                      timezone=timezone,
                      datetime_template=datetime_template)

import sqlalchemy
from sqlalchemy_utils import database_exists, create_database

import sunpeek.components as cmp
from sunpeek.common import utils
import sunpeek.definitions

db_url = utils.get_db_conection_string()


def init_db():
    assert not database_exists(db_url), f"Database {db_url.split('/')[-1]} already exists, please set HIT_DB_NAME to a " \
                                        f"database doesn't exist yet, it will be created for you"

    utils.sp_logger.info(f'[init_db] Attempting to setup DB on {db_url}')
    engine = sqlalchemy.create_engine('/'.join(utils.get_db_conection_string().split('/')[:-1]))
    with engine.begin() as con:
        le = len(list(con.execute(sqlalchemy.text("select extname from pg_extension where extname='timescaledb';"))))
        assert le == 1, "Timescaledb extension must be installed and available"
    engine.dispose()

    create_database(db_url)

    cmp.make_tables(utils.db_engine)

    with utils.S() as session:
        #Add collector types
        for item in sunpeek.definitions.collector_types.all_definitions:
            session.add(item)

        #Add fluids
        for item in sunpeek.definitions.fluid_definitions.all_definitions:
            session.add(item)

        session.commit()
        session.expunge_all()


if __name__ == '__main__':
    init_db()

import copy
from sqlalchemy import exc

import sunpeek.components as cmp
from sunpeek.common.errors import ConfigurationError, DuplicateNameError

def _check_colltype_in_db(session, col_type_name):
    if session is not None:
        import sqlalchemy.exc
        try:
            session.query(cmp.CollectorType).filter(cmp.CollectorType.name == col_type_name).one()
            return True
        except sqlalchemy.exc.NoResultFound:
            return False
    return False


def make_full_plant(conf, session=None):
    conf = copy.deepcopy(conf)
    collector_types = {}
    if 'collector_types' in conf:
        col_types = conf['collector_types']
        for col_type in col_types:
            test_type = col_type.pop('test_type')
            if _check_colltype_in_db(session, col_type['name']):
                type_obj = col_type['name']
            elif test_type in ['SST', "static"]:
                type_obj = cmp.CollectorTypeSST(**col_type)
            elif test_type in ['QDT', "dynamic"]:
                type_obj = cmp.CollectorTypeQDT(**col_type)
            else:
                raise ConfigurationError("CollectorType test_type parameter must be one of 'SST', 'static', 'QDT' or 'dynamic'")
            collector_types[type_obj.name] = type_obj
    if 'plant' in conf:
        conf = conf['plant']
        for array in conf['arrays']:
            if array['collector_type'] in collector_types.keys():
                array['collector_type'] = collector_types[array['collector_type']]

    plant = cmp.Plant(**conf)

    if session is not None:
        session.add(plant)
        session.rollback()

    return plant


def make_and_store_plant(conf, session):
    plant = make_full_plant(conf, session)
    session.add(plant)

    try:
        session.commit()
    except exc.IntegrityError:
        raise DuplicateNameError(f'Plant with name "{plant.name}" already exists.')

    return plant

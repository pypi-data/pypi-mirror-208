"""
.. codeauthor:: Marnoch Hamilton-Jones <m.hamilton-jones@aee.at>
.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
"""

import numpy as np
import sqlalchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Float, Identity, ARRAY
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.orm
import sqlalchemy.exc
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
import sqlalchemy.event
import enum

from sunpeek.common.unit_uncertainty import Q
import sunpeek.common.unit_uncertainty as uu
from sunpeek.common.errors import ConfigurationError


ORMBase = declarative_base()


class ComponentParam:
    """Used to define parameters which are represented by Quantities, with optional limit checking.  
    
    Attributes
    ----------
    unit: compatible unit
    minimum: value of the paramters should not be below this
    maximum: value of the paramters should not be above this
    type: either "scalar" or "array", defaults to used to create the correct database column types and apply checks correctly.
    """
    
    def __init__(self, unit: str = None, minimum: float = -np.Inf, maximum: float = np.Inf, type: str = 'scalar'):
        # self.name = name
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum
        self.type = type


class AttrSetterMixin:
    name = None
    defer_configure_virtuals = False

    @classmethod
    def define_component_attrs(cls):
        for sub_cls in cls.all_subclasses():
            params = {attr: obj for attr, obj in sub_cls.__dict__.items() if isinstance(obj, ComponentParam)}
            for attr, obj in params.items():
                # delattr(sub_cls, attr)
                sub_cls.add_component_attr(attr, obj.unit, obj.minimum, obj.maximum, obj.type)

    @classmethod
    def add_component_attr(cls, name, unit=None, minimum=-np.Inf, maximum=np.Inf, type='scalar'):
        if type == 'scalar':
            setattr(cls, '_{}_mag'.format(name), Column(Float))
        elif 'array':
            setattr(cls, '_{}_mag'.format(name), Column(ARRAY(Float)))
        setattr(cls, '_{}_unit'.format(name), Column(String))
        prop = property(fset=lambda cls, value: cls.set_component_attribute(name, value, type),
                        fget=lambda cls: cls.get_component_attribute(name))
        setattr(cls, name, prop)
        if not hasattr(cls, '_attr_props'):
            cls._attr_props = {}
        cls._attr_props[name] = {'unit': unit, 'minimum': minimum, 'maximum': maximum}
        # print (self.attr_props[name])

    @classmethod
    def all_subclasses(cls, c=None):
        if c is None: c = cls
        return set(c.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.all_subclasses(c)])

    def _check_value(self, name, value, type):
        unit = self._attr_props[name]['unit']

        uu.assert_compatible(value.units, unit)

        val = value.to(unit).magnitude
        min = self._attr_props[name]['minimum']
        max = self._attr_props[name]['maximum']

        if type == 'scalar' or type is None:
            if isinstance(value.magnitude, np.ndarray):
                raise ConfigurationError("Attempting to assign an array quantity to a scalar type parameter")
            if val < min:
                raise ConfigurationError(f"attempting to set a value for attribute {name} that is less than the minimum of {min}{unit}")
            if val > max:
                raise ConfigurationError(f"attempting to set a value for attribute {name} that is greater than the maximum of {max}{unit}")

        if type == 'array':
            if not isinstance(value.magnitude, np.ndarray):
                raise ConfigurationError("Attempting to assign an array quantity to a scalar type parameter")
            if (val < min).any():
                raise ConfigurationError(f"attempting to set a value for attribute {name} that is less than the minimum of {min}{unit}")
            if (val > max).any():
                raise ConfigurationError(f"attempting to set a value for attribute {name} that is greater than the maximum of {max}{unit}")

    def set_component_attribute(self, name, value, type):
        if value is not None:
            value = uu.parse_quantity(value)
            if not self._attr_props[name]['unit'] == 'no_check':
                self._check_value(name, value, type)

            if type == 'scalar' or type is None:
                mag = value.magnitude
            elif type == 'array':
                mag = value.magnitude.tolist()
            else:
                raise ValueError("type must be either 'scalar' or 'array'")

            setattr(self, '_{}_mag'.format(name), mag)
            setattr(self, '_{}_unit'.format(name), str(value.units))
        else:
            # setattr(self, name, None)
            setattr(self, '_{}_mag'.format(name), None)
            setattr(self, '_{}_unit'.format(name), None)
        if getattr(self, 'plant', None) is not None and (self.__class__.__name__ != 'Sensor'):
            # Update whether virtual sensor can be calculated with new plant information
            if not self.defer_configure_virtuals:
                self.plant.config_virtuals()

    def get_component_attribute(self, name):
        if self.__getattribute__('_{}_mag'.format(name)) is None:
            return None
        return Q(self.__getattribute__('_{}_mag'.format(name)), self.__getattribute__('_{}_unit'.format(name)))

    def __getattr__(self, item):
                    # print('attr==sens')
        if (item == "sensors") or ('_AssociationProxy__sensor_map' in item) or (item in ['_sa_instance_state', '_proxy_dicts']):
            raise AttributeError

        try:
            return self.sensors[item]
        except KeyError:
            if item in self.sensor_slots.keys():
                return None
            else:
                raise AttributeError(f"{item} not found in component {self}.")
        except (AttributeError, AssertionError, sqlalchemy.exc.InvalidRequestError) as ex:
            raise AttributeError(f"{item} not found in component {self}. Original exception: {ex}")

    def __str__(self):
        try:
            if self.name is not None:
                return 'HarvestIT {} component called {}'.format(self.__class__.__name__, self.name)
            else:
                return 'HarvestIT {} object'.format(self.__class__.__name__)
        except sqlalchemy.exc.InvalidRequestError:
            return "unknown SunPeek component"

    def __repr__(self):
        return self.__str__()

    def __dir__(self):
        try:
            return list(self.sensor_slots.keys()) + list(super().__dir__())
        except AttributeError:
            return super().__dir__()


class AccuracyClass(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class InstallCondition(enum.Enum):
    perfect = "perfect"
    fair = "fair"
    bad = "bad"


class IsVirtual(enum.Enum):
    never = "never"
    possible = "possible"
    always = "always"
    
    
class ResultStatus(enum.Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class SensorMap(ORMBase):
    """Class which defines the many-to-many mapping table and performs required logic to map Sensor objects to sensor
    channels on components.
    The `sensor_type` argument to the __init__ method determines the SensorType that will be attached to the sensor.
    If a sensor type has already been attached, attempting to create another mapping with a different type, a ConfigurationError
    will be raised.
    When a SensorMap is created, the sensor_type is not attached immediately. Instead, the `sensor_type_name` attribute
    of the sensor is set. When the SensorMap object is attached to a database session, a lookup is performed against the
    sensor_types table, and an appropriate SensorType object loaded and attached to the sensor.

    Attributes
    ----------

    sensor : py:class:sunpeek.components.sensor.Sensor
        The sensor object to be mapped
    slot_name: str
        The name of the sensor channel being mapped to, e.g. `te_amb`
    array : physical.Array
        Array object, if the mapping is to an array
    plant : physical.Plant
        Plant object, if the mapping is to a plant
    heat_exchanger : helpers.pyHeatExchanger
        HeatExchanger object, if the mapping is to a hx
    """
    __tablename__ = 'sensor_map'

    id = Column(Integer, Identity(0), primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id', ondelete="CASCADE"))
    slot_name = Column(String)

    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"))
    array_id = Column(Integer, ForeignKey('arrays.id', ondelete="CASCADE"))
    heat_exchanger_id = Column(Integer, ForeignKey('heat_exchangers.id', ondelete="CASCADE"))
    # row_id = Column(Integer, ForeignKey('rows.id'))

    # reference to the "Sensor" object
    sensor = relationship("Sensor", foreign_keys=[sensor_id], backref="_mappings")

    # Create association proxy relationships to parent components
    array = relationship("Array",
                         backref=backref("_sensor_map",
                                         collection_class=attribute_mapped_collection("slot_name"),
                                         cascade="all, delete-orphan"))
    plant = relationship("Plant",
                         backref=backref("_sensor_map",
                                         collection_class=attribute_mapped_collection("slot_name"),
                                         cascade="all, delete-orphan"))
    heat_exchanger = relationship("HeatExchanger",
                                  backref=backref("_sensor_map",
                                                  collection_class=attribute_mapped_collection("slot_name"),
                                                  cascade="all, delete-orphan"))

    @property
    def component(self):
        for comp in [self.array, self.plant, self.heat_exchanger]:
            if comp is not None:
                return comp

    def __init__(self, slot_name: str, sensor, sensor_type, component):
        if sensor is None:
            return
        self.slot_name = slot_name

        if isinstance(sensor, str):
            raise ConfigurationError(f'SensorMap was passed a string instead of a sensor obejct. This could be because '
                                     f'channel {slot_name} of {component} was mapped to a raw sensor that does not exist.')
            # This should have been excluded by _on_array_append
        if component.plant is None:
            raise ConfigurationError(f'Cannot map sensor to channel {slot_name} of component {component} because '
                                     f'component.plant is None.')

        if isinstance(sensor_type, str):
            type_name = sensor_type
        else:
            type_name = sensor_type.name
        if sensor.sensor_type is None:
            # sensor.sensor_type = type_name
            pass
        # elif sensor.sensor_type.name == type_name:
        #     pass
        elif sensor.sensor_type.name != type_name:
            raise ConfigurationError(
                f'Sensor {sensor.raw_name} already has type "{sensor.sensor_type.name}". Mapping to "{slot_name}" of '
                f'{component} requires type "{type_name}". Check your config.')

        sensor.plant = component.plant
        # else:
        #     raise ConfigurationError(f'Sensor {sensor.raw_name} mapping to "{slot_name}" of {component}. There appears '
        #                              f'to be a mismatch between sensor types and type_names names. '
        #                              f'Type: "{sensor.sensor_type}", Type name: "{type_name}"')

        self.sensor = sensor
        setattr(self,
                {r.mapper.class_.__name__: r.key for r in SensorMap.__mapper__.relationships}
                [component.__class__.__name__], component)

        # In case the attribute for channel name was already set to None, remove it so that __getattr__ looks in sensors
        component.__dict__.pop(slot_name, None)
        sensor.plant = component.plant


# class Row(AttrSetterMixin, ORMBase):
#     """
#     Implements a single collector row with its inlet and outlet temperatures, as part of an Array.
#
#     Note
#     ----
#     An array may consist of several rows. Row components are useful if inlet or outlet temperatures (`te_in`,
#     `te_out`) are measured only at row level, and no measurements are available for the whole array. In this case,
#     one option would be to set the array level `te_in` | `te_out` as the average of all the array's rows.
#     Instantiating a Row only makes sense if either `te_in` or `te_out` (or both) are available measurement channels.
#
#     Attributes
#     ----------
#     array : Array object
#         Array to which the Row belongs.
#     te_in : Sensor, optional
#         Inlet / return temperature of collector row.
#     te_out : Sensor, optional
#         Outlet / flow temperature of collector row.
#     """
#     __tablename__ = 'rows'
#
#     id = Column(Integer, Identity(0), primary_key=True)
#     array_id = Column(Integer, ForeignKey(Array.id))
#     array = relationship("Array")
#
#     sensors = association_proxy("sensor_map", "sensor")
#
#     def __init__(self, array=None, te_in=None, te_out=None):
#         self.array = array
#         self.te_in = te_in
#         self.te_out = te_out
#
#         SensorMap('te_in', te_in, 'fluid_temperature', component=self)
#         SensorMap('te_out', te_out, 'fluid_temperature', component=self)





# array_results_association_table = sqlalchemy.Table('array_results_association', ORMBase.metadata,
#                                                    Column('result_id', primary_key=True),
#                                                    Column('result_time', primary_key=True),
#                                                    Column('array_id', ForeignKey('arrays.id'), primary_key=True),
#                                                    ForeignKeyConstraint(["result_id", "result_time"], ["pc_results.id",
#                                                                                                        "pc_results.datetime_eval_done"]),
#                                                    )


# AttrSetterMixin.define_component_attrs()


# TODO: make results table a hypertable, might not be possible due to Timescale limitiations: https://github.com/timescale/timescaledb/issues/498
# sqlalchemy.event.listen(
#     PCMethodOutput.__table__,
#     'after_create',
#     sqlalchemy.DDL(f"SELECT * FROM create_hypertable('{PCMethodOutput.__tablename__}', 'datetime_eval_done');")
# )
#
# sqlalchemy.event.listen(
#     PCMethodOutput.__table__,
#     'after_create',
#     sqlalchemy.DDL(f"CREATE INDEX ON "
#                    f"{PCMethodOutput.__tablename__}(plant_id, datetime_eval_done);")
# )
#
# sqlalchemy.event.listen(
#     PCMethodOutput.__table__,
#     'after_create
#     sqlalchemy.DDL(f"CREATE INDEX ON "
#                    f"{PCMethodOutput.__tablename__}(plant_id, datetime_eval_start, datetime_eval_end, datetime_eval_done);")
# )

def make_tables(engine):
    """Uses the table definitions contained in the component classes to create DB tables"""
    ORMBase.metadata.create_all(engine)

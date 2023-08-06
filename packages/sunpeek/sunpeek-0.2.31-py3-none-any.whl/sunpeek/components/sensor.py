import pandas as pd
import sqlalchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum, Identity, JSON
from sqlalchemy.orm import relationship

import sunpeek.common.unit_uncertainty as uu
from sunpeek.common.unit_uncertainty import Q, units
from sunpeek.common.errors import ConfigurationError, VirtualSensorConfigurationError, VirtualSensorCalculationError, \
    DuplicateNameError
from sunpeek.common.utils import sp_logger
from sunpeek.components.helpers import ORMBase, AttrSetterMixin, AccuracyClass, InstallCondition, ComponentParam
from sunpeek.components import sensor_types as st


class SensorInfo(ORMBase):
    __tablename__ = 'sensorinfo'

    id = Column(Integer, Identity(0), primary_key=True)
    _info = Column(JSON)
    sensor_id = Column(Integer, ForeignKey('sensors.id', ondelete="CASCADE"))
    sensor = relationship("Sensor")

    def __init__(self, **items):
        self._info = {}
        for k, v in items.items():
            if isinstance(v, Q):
                self[k] = {'magnitude': v.magnitude, 'units': str(v.units)}
            else:
                self[k] = v

    def __getitem__(self, item):
        item = self._info[item]
        if isinstance(item, (dict, list)):
            if ('magnitude' and 'units') in item:
                return Q(item['magnitude'], item['units'])
            if len(item) == 2:
                return Q(item[0], item[1])

        return self._info[item]

    def __setitem__(self, key, value):
        self._validate(key, value)
        self._info[key] = value

    @property
    def sensor_type(self):
        if self.sensor is None:
            return None
        return self.sensor.sensor_type

    @property
    def attr_props(self):
        if self.sensor_type is not None:
            return self.sensor_type.info_checks
        else:
            return {}

    def _validate(self, key, value):
        if key in self.attr_props:
            if not self.attr_props[key].get('no_check', False):
                uu.assert_compatible(value.units, self.attr_props[key]['unit'])
                assert self.attr_props[key]['minimum'] <= value.to(self.attr_props[key]['unit']).magnitude
                assert value.to(self.attr_props[key]['unit']).magnitude <= self.attr_props[key]['maximum']

    def validate_all(self):
        if self.sensor_type is None:
            raise ValueError(
                'SensorInfo object must have a sensor_type available to perform validation. This error might be caused'
                'by the parent sensor not having been mapped yet and not having a sensor_type given explicitly')
        for k in self._info.keys():
            self._validate(k, self[k])

    def __str__(self):
        return str(self._info)

    def __repr__(self):
        return f'SensorInfo{self.__str__()}'


class Sensor(ORMBase, AttrSetterMixin):
    __tablename__ = 'sensors'

    id = Column(Integer, Identity(0), primary_key=True)
    raw_name = Column(String)
    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"))
    plant = relationship("Plant", back_populates='raw_sensors')
    _given_sensor_type = Column(String)
    # hardware_type_id = Column(Integer, ForeignKey('hardware_types.id'))
    # hardware_type = relationship("HardwareType")
    description = Column(String)
    _native_unit = Column(String)
    is_virtual = Column(Boolean, nullable=False)
    # is_calculated = Column(Boolean, nullable=False)
    can_calculate = Column(Boolean, nullable=False)
    _accuracy_class = Column(Enum(AccuracyClass))
    _installation_condition = Column(Enum(InstallCondition))
    _lower_replace_min = ComponentParam('no_check')
    _lower_replace_max = ComponentParam('no_check')
    lower_replace_value = ComponentParam('no_check')
    _upper_replace_min = ComponentParam('no_check')
    _upper_replace_max = ComponentParam('no_check')
    upper_replace_value = ComponentParam('no_check')
    info = relationship("SensorInfo", back_populates='sensor', uselist=False, cascade="all, delete",
                        passive_deletes=True, )

    __table_args__ = (
        sqlalchemy.UniqueConstraint('raw_name', 'plant_id'),
    )

    def __init__(self, raw_name, native_unit, plant=None, description=None, accuracy_class=None,
                 installation_condition=None, hardware_type=None, sensor_type=None,
                 is_virtual=False, can_calculate=False, value_replacements={}, info={}):
        self.raw_name = raw_name
        self.description = description
        self.accuracy_class = accuracy_class
        self._installation_condition = installation_condition
        self.plant = plant
        self.info = info
        self.hardware_type = hardware_type
        self.sensor_type = sensor_type
        self.is_virtual = is_virtual
        self.can_calculate = can_calculate
        # self.is_calculated = False
        self.info = info
        self.native_unit = native_unit
        self.value_replacements = value_replacements

    @property
    def native_unit(self):
        if self._native_unit is not None and self._native_unit != 'None':
            return getattr(units, self._native_unit)
        elif self.sensor_type is not None:
            return units[self.sensor_type.compatible_unit_str]
        else:
            return None

    @native_unit.setter
    def native_unit(self, native_unit_str):
        sensor_type_unit = None
        if self.sensor_type is not None and self.sensor_type.compatible_unit_str is not None:
            sensor_type_unit = self.sensor_type.compatible_unit_str

        # None unit: get from sensor_type. Relevant for virtual sensors
        if native_unit_str is None:
            if sensor_type_unit is None:
                # TODO reactivate this Exception?
                pass
                # raise TypeError('Sensor needs either a "native_unit" or a ".sensor_type.compatible_unit_str".')
            native_unit = sensor_type_unit
        else:
            # Check unit exists
            try:
                native_unit = units[native_unit_str]
            except uu.pint.errors.UndefinedUnitError:
                raise uu.pint.errors.UndefinedUnitError(
                    "'sensor_native_unit' must be a valid python pint library unit string")
            # Make sure native_unit is compatible with SensorType unit
            if sensor_type_unit is not None:
                uu.assert_compatible(sensor_type_unit, native_unit)
                # raise IncompatibleUnitError(f'Sensor unit {native_unit} is not compatible with SensorType expected '
                #                             f'unit {str(self.sensor_type.min_limit.units)}')
        # normalise unit name, store as string for DB compatibility
        self._native_unit = str(native_unit)

    @property
    def native_unit_str(self):
        return str(self.native_unit)

    @sqlalchemy.orm.validates('info')
    def _set_info(self, _, info):
        if isinstance(info, SensorInfo):
            return info
        elif isinstance(info, dict):
            return SensorInfo(**info)
        elif info is None:
            return SensorInfo()
        else:
            raise TypeError(f"'info' must be either a SensorInfo object or a dict, got type {type(info)}")

    @sqlalchemy.orm.validates('plant')
    def _verify_plant(self, _, plant):
        if plant is None:
            return plant
        # Check for sensors with duplicate name in plat already
        raw_names = [s.raw_name.lower() for s in plant.raw_sensors]
        existing = raw_names.index(self.raw_name.lower()) if self.raw_name.lower() in raw_names else None
        if existing is not None and self != plant.raw_sensors[existing]:  # Allow re-adding self
            raise DuplicateNameError(f"A sensor with raw_name {self.raw_name} already exists. The names of sensors and"
                                     f" columns in raw data must be unique. Note that sensor names are always converted"
                                     f" to lowercase.")
        return plant

    def __str__(self):
        return f"HarvestIT Sensor, raw_name: {self.raw_name}"

    def __repr__(self):
        return self.__str__()

    @property
    def installation_condition(self):
        if self._installation_condition is not None:
            return self._installation_condition
        else:
            return

    @property
    def accuracy_class(self):
        # if self.hardware_type is not None:
        #     return self.hardware_type.accuracy_class
        if self._accuracy_class is not None:
            return self._accuracy_class
        else:
            return self.plant.plant_measurement_accuracy

    @accuracy_class.setter
    def accuracy_class(self, val):
        if isinstance(val, AccuracyClass):
            self._accuracy_class = val
        elif val is not None:
            self._accuracy_class = AccuracyClass[val]

    @property
    def sensor_type(self):
        if self._given_sensor_type is not None:
            return getattr(st, self._given_sensor_type)
        elif self.is_mapped:
            return self._mappings[0].component.sensor_slots[self._mappings[0].slot_name].sensor_type
        else:
            return None

    @sensor_type.setter
    def sensor_type(self, val):
        if val is None:
            return
        if isinstance(val, str):
            try:
                val = getattr(st, val)
            except AttributeError:
                raise ConfigurationError(f'{val} is not a known sensor type')

        self._given_sensor_type = val.name
        self.info.validate_all()
        if self.is_virtual:
            self.native_unit = val.compatible_unit_str

    @property
    def data(self):
        """Accessor for sensor data.

        Returns
        -------
        pandas Series object with 1 data column and DateTimeIndex depending on self.plant.context properties.

        Notes
        -----
        Does not change data time index, e.g. values are not resampled. To resample, use sensor.get_data()
        """
        if self.plant is None:
            raise ConfigurationError('Cannot access sensor.data because the sensor does not have a plant associated.')

        return self.plant.context.get_sensor_data(sensor=self)

    @property
    def is_mapped(self):
        if len(self._mappings) > 0:
            return True
        return False

    @property
    def value_replacements(self):
        reps = {'upper': (self._upper_replace_min, self._upper_replace_max, self.upper_replace_value),
                'lower': (self._lower_replace_min, self._lower_replace_max, self.lower_replace_value)}

        has_sensor_type = (self.sensor_type is not None)
        all_none = lambda k: all((x is None for x in reps[k]))
        if has_sensor_type and all_none('upper'):
            reps['upper'] = (self.sensor_type.upper_replace_min, self.sensor_type.upper_replace_max,
                             self.sensor_type.upper_replace_value)
        if has_sensor_type and all_none('lower'):
            reps['lower'] = (self.sensor_type.lower_replace_min, self.sensor_type.lower_replace_max,
                             self.sensor_type.lower_replace_value)

        return reps

    @property
    def value_replacements__native(self):
        """Return self.value_replacements, but with all Quantities converted to floats in self.native_unit
        """
        reps = self.value_replacements
        reps_native = {}
        convert = lambda x: x.m_as(self.native_unit) if x is not None else None
        for key in ['lower', 'upper']:
            reps_native[key] = (convert(el) for el in reps[key])

        return reps_native

    @value_replacements.setter
    def value_replacements(self, val):
        # assert isinstance(val, dict), 'Value replacement expected to be a dict.'
        # Changing value_replacements potentially affects cleaned value
        if self.plant is not None:
            self.plant.context.reset_cache()

        def check_tuple(s, d, key):
            if len(d[key]) != 3:
                raise ValueError(
                    'To define a sensor replacement interval, pass a dictionary with a 3-value tuple representing the '
                    'left and right interval boundaries and the replacement value.')
            left, right, replace = d[key]
            for x in [left, right, replace]:
                if (x is not None) and (not x.is_compatible_with(s.native_unit)):
                    raise ValueError(
                        f'Cannot set replacement interval because unit is not compatible with sensor native_unit '
                        f'{self.native_unit_str}')
            if (left is not None) and (right is not None) and (left > right):
                raise ValueError(
                    'In a lower replacement interval, the lower limit cannot be larger than the upper limit.')
            if (left is None) and (right is None) and (replace is not None):
                raise ValueError(
                    'Cannot set replacement value for a replacement interval, because both left or right interval '
                    'boundaries are None.')
            if (replace is None) and (left is not None) and (right is not None):
                raise ValueError(
                    'Cannot define replacement interval, because replacement is None while both interval limits '
                    'are not None.')
            if key == 'lower':
                if (right is None) and (left is not None) and (replace is not None):
                    raise ValueError(
                        'Cannot define lower replacement interval, because right interval boundary is None '
                        'while left interval limit and replacement value are not None.')
            elif key == 'upper':
                if (left is None) and (right is not None) and (replace is not None):
                    raise ValueError(
                        'Cannot define upper replacement interval, because left interval boundary is None '
                        'while right interval limit and replacement value are not None.')
            return left, right, replace

        if 'lower' in val:
            left, right, replace = check_tuple(self, val, 'lower')
            self._lower_replace_min = left
            self._lower_replace_max = right
            self.lower_replace_value = replace
        else:
            self._lower_replace_min = None
            self._lower_replace_max = None
            self.lower_replace_value = None

        if 'upper' in val:
            left, right, replace = check_tuple(self, val, 'upper')
            self._upper_replace_min = left
            self._upper_replace_max = right
            self.upper_replace_value = replace
        else:
            self._upper_replace_min = None
            self._upper_replace_max = None
            self.upper_replace_value = None

    def m_as(self, unit):
        """Shortcut to convert self.data from pd.Series with dtype pint to numeric array.
        Method `m_as` exists also for pint.Quantity objects, so this enables same syntax for pint.Quantity and
        pd.Series. """
        # return self.data.pint.to(unit).astype('float64').to_numpy()
        return self.s_as(unit).to_numpy()

    def s_as(self, unit):
        """Shortcut to convert self.data from pd.Series with dtype pint to normal pd.Series, with numeric values
        converted to unit.
        """
        return self.data.pint.to(unit).astype('float64')

    def q_as(self, unit):
        """Shortcut to convert self.data from pd.Series with dtype pint to pint.Quantity array, with numeric values
        converted to unit.
        """
        return Q(self.m_as(unit), unit)

    def plot(self):
        """Create a simple development plot method for Sensor data."""
        # pd.set_option("plotting.backend", "plotly")
        # pio.renderers.default = 'browser'
        return self.data.astype('float64').plot().show()

    def update(self, data: pd.Series = None):
        """Save calculation results of virtual sensors to Context datasource.

        Parameters
        ----------
        data : pd.Series, Data to be set as self.data

        Raises
        ------
        VirtualSensorError
            If called on a normal (not virtual) sensor, so if self.virtual_sensor == False
        """
        if not self.is_virtual:
            raise VirtualSensorConfigurationError(
                'Can only update for virtual sensors, but got called on a regular sensor.')

        if data is not None:
            try:
                data.pint
            except AttributeError:
                raise VirtualSensorCalculationError(
                    'Calculated virtual sensor data expected to be pd.Series with dtype pint.')
            if not self.native_unit.is_compatible_with(data.pint.units):
                raise VirtualSensorCalculationError(
                    f'Calculated virtual sensor data not compatible with expected unit {self.native_unit}.')
            # Trying to minimize the changes made to sensor object: don't overwrite sensor native_unit
            # self.native_unit = uu.get_unit_string(data)
            data = data.pint.to(self.native_unit)

        # sp_logger.debug(f"[sensor.update] Storing data for sensor {self.raw_name }")
        self.plant.context.store_data(self, data)
        # If data is None / a vsensor calculation was not possible (for whatever reason), Context will store an all-NaN
        # series.

    def get_orientation(self):
        """Returns dictionary with array's "tilt" and "azim" values converted to deg, for radiation calculations.
        """
        return {'tilt': self.info['tilt'].m_as('deg'),
                'azim': self.info['azim'].m_as('deg')}

#
# @sqlalchemy.event.listens_for(Session, "transient_to_pending")
# def _set_sensor_types(session, inst):
#     if isinstance(inst, SensorMap):
#         try:
#             with session.no_autoflush:
#                 type_def = session.query(SensorType).filter(SensorType.name == inst.sensor.sensor_type_name).one()
#         except sqlalchemy.exc.NoResultFound:
#             raise ConfigurationError(f'No sensor type definition found matching{inst.sensor.sensor_type_name} while '
#                                      f'setting type for sensor: {inst.sensor.raw_name}')
#         except sqlalchemy.exc.MultipleResultsFound:
#             raise ConfigurationError(f'Multiple sensor type definitions found matching {inst.sensor.sensor_type_name} '
#                                      f'while setting type for sensor: {inst.sensor.raw_name}')
#         inst.sensor.sensor_type = type_def

import uuid
from sqlalchemy.ext.associationproxy import association_proxy
from typing import Union, Dict
import dataclasses
from sunpeek.common.errors import ConfigurationError
from sunpeek.common.unit_uncertainty import Q
from sunpeek.common.utils import VerifyValidateMode
from sunpeek.components import types
from sunpeek.components.helpers import IsVirtual, AttrSetterMixin, SensorMap
from sunpeek.components.sensor import Sensor


@dataclasses.dataclass
class SensorSlot():
    """
    A pydantic class used to hold and validate information on a component sensor slot.
    
    Parameters
    ----------
    name : str
        The name of the slot, which beahvaes like a component attribute and can be used to access the mapped sensor from 
        the component. e.g. te_amb. `name` only needs to be unique and understandable in the context of a specific
        component, e.g. the `tp` slot of a plant includes the total power of all arrays, whereas `tp` of an array is
        just that array's power.
    descriptive_name : str
        A longer more descriptive name, e.g. for display to a user in a front end client. Limited to 24 characters
    description : str
        A description of the purpose and use of the slot.
    virtual : enum
        Whether the sensor for a slot is always virtual, can be virtual given certain conditions, or is never virtual
    """

    name: str
    sensor_type: types.SensorType
    descriptive_name: Union[str, None] = None
    virtual: IsVirtual = IsVirtual.never
    description: Union[str, None] = None
    #
    # def __init__(self,
    #              name: str,
    #              sensor_type: str,
    #              descriptive_name: str,
    #              virtual: Union[IsVirtual, str],
    #              description: str = None):
    #     super().__init__(name=name, sensor_type=sensor_type, descriptive_name=descriptive_name, virtual=virtual,
    #                      description=description)


class Component(AttrSetterMixin):
    """Abstract Class to be used for physical components of a Plant"""

    sensor_slots: Dict[str, SensorSlot] = {}
    sensors = association_proxy("_sensor_map", "sensor")

    def __setattr__(self, key, value):
        if key in self.sensor_slots:
            return self.map_sensor(value, key)
        return super().__setattr__(key, value)

    def set_sensors(self, **kwargs):
        self.defer_configure_virtuals = True
        for slot_name, sensor in kwargs.items():
            self.map_sensor(sensor, slot_name)
        self.defer_configure_virtuals = False
        if self.plant is not None:
            self.plant.config_virtuals()

    def map_sensor(self, sensor: Sensor, slot_name: str):
        """Maps sensor to slot_name of given component, including some sanity checks.
        """
        real_slots = [slot.name for slot in self.get_real_slots()]
        if sensor is not None and slot_name in real_slots:
            SensorMap(slot_name, sensor, component=self,
                      sensor_type=self.sensor_slots[slot_name].sensor_type)
        elif (not self.sensors[slot_name].is_virtual if self.sensors.get(slot_name) is not None else False):
            # If slot is not empty and sensor currently in slot is not virtual
            # TODO: Maybe replace this using association_proxy, see #288
            # if slot_name in self.sensors:
            del self.sensors[slot_name]._mappings[self.sensors[slot_name]._mappings.index(self.sensor_map[slot_name])]
            del self.sensor_map[slot_name]

        if not self.defer_configure_virtuals and self.plant is not None:
            self.plant.config_virtuals()
        return

    def map_vsensor(self, slot_name: str, can_calculate: bool = True):
        """Create virtual Sensor and map it to component.slot_name, or map None if can_calculate is not met."""
        if not self.has_virtual_slot_named(slot_name):
            raise ConfigurationError(f'Cannot map virtual sensor because slot {slot_name} of {self} '
                                     f'does not accept virtual sensors.')
        try:
            sensor = self.sensors[slot_name]
        except KeyError:
            sensor = None
        # Sensor already mapped? Update only
        if sensor is not None and not sensor.is_virtual:
            return  # Do not overwrite existing real sensor
        elif sensor is not None:
            sensor.can_calculate = can_calculate
            # TODO could return reason _why_ this vsensor cannot be calculated, e.g. for WebUI
            return

        vsensor_name = f"{slot_name}__virtual__{self.__class__.__name__}_{self.name}".replace(' ', '_').lower()
        if self.plant.get_raw_sensor(vsensor_name) is not None if self.plant is not None else False:
            # Plant is not None and vsensor with matching name already exists
            vsensor = self.plant.get_raw_sensor(vsensor_name)
            vsensor.can_calculate = can_calculate
        else:
            # Create virtual sensor
            # Needs to store compatible_unit of sensor_type, so it can later check if vsensor calc results are ok.
            vsensor = Sensor(is_virtual=True,
                             can_calculate=can_calculate,
                             plant=self.plant,
                             raw_name=vsensor_name,
                             # a huge number of tests fail if vsensor doesn't know its compatible unit
                             native_unit=self.sensor_slots[slot_name].sensor_type.compatible_unit_str
                             # native_unit=get_sensor_type(self._get_type_name(slot_name)).compatible_unit_str,
                             )

        SensorMap(slot_name, vsensor, component=self, sensor_type=self.sensor_slots[slot_name].sensor_type)

    def has_virtual_slot_named(self, slot_name):
        """Assert component has a (possibly or always) virtual sensor slot named slot_name.
        """
        vnames = [slot.name for slot in self.sensor_slots.values() if slot.virtual != IsVirtual.never]
        return slot_name in vnames

    @classmethod
    def get_real_slots(cls):
        """Get component's slot names for (possibly or always) real (not virtual) sensors
        """
        return [slot for slot in cls.sensor_slots.values() if slot.virtual != IsVirtual.always]

    def assert_verify_validate(self, check_mode: str, *attribs: str):
        """Calls verify_validate, raises AssertionError if verify / validate failed.
        """
        response = self.verify_validate(check_mode, *attribs)
        assert response[0], response[1]

    def verify_validate(self, check_mode: str, *attribs: str):
        """Return True if component attributes named `attribs` are wither ComponentParam / Quantity or
        - if check_mode=='configured': is a virtual Sensor and .can_calculate
        - if check_mode=='calculated': is a virtual Sensor and .validate_data

        Parameters
        ----------
        check_mode : 'configured' or 'calculated'
        attribs : str, keys of self.sensor_slots or ComponentParam attributes

        Returns
        -------
        tuple
            bool: 1 bool value, True only if ok for all attribs.
            list: list of sensor_slots which broke the conditions.
        """
        # assert check_mode in ['configured', 'calculated'], f'Unknown "check_mode" parameter: {check_mode}.'
        assert check_mode.lower() in [el.name for el in VerifyValidateMode], \
            f'Unknown "check_mode" parameter: {check_mode}.'
        if check_mode == VerifyValidateMode.validate:
            assert len(self.plant.time_index) > 0, 'No data found for plant, "plant.time_index" is empty.'

        problem_slots = []
        for attrib in attribs:
            try:
                sensor_or_componentparam = getattr(self, attrib)
            except AttributeError:
                problem_slots.append(attrib)
                continue
            # Sensor
            if attrib in self.sensor_slots:
                if sensor_or_componentparam is None:
                    problem_slots.append(attrib)
                    continue
                assert isinstance(sensor_or_componentparam, Sensor)
                s = sensor_or_componentparam
                if s.is_virtual:
                    if (check_mode == VerifyValidateMode.verify) and (not s.can_calculate):
                        problem_slots.append(attrib)
                    elif (check_mode == VerifyValidateMode.validate) and s.data.notna().sum() == 0:
                        problem_slots.append(attrib)
            # ComponentParam
            elif isinstance(sensor_or_componentparam, Q):
                if sensor_or_componentparam is None:
                    problem_slots.append(attrib)
            # all others allow gracefully
            else:
                problem_slots.append(attrib)
        return (len(problem_slots) == 0), problem_slots

    # def can_calculate(self, *attribs: str):
    #     """Return True if all component attributes are
    #     - valid real Sensors or virtual Sensors with .can_calculate==True
    #     - or ComponentParams
    #     """
    #     all_ok, problem_slots = self.verify_validate(check_mode='configured', *attribs)
    #     return all_ok
    #
    # def validate_data(self, *attribs: str):
    #     """Return True if all attribs are valid real Sensors or virtual Sensors with .validate_data==True"""
    #     all_ok, problem_slots = self.verify_validate(check_mode='calculated', *attribs)
    #     return all_ok

    @property
    def sensor_map(self):
        return self._sensor_map

    @sensor_map.setter
    def sensor_map(self, str_map):
        if isinstance(str_map, dict):
            if not str_map:  # Nothing to do, avoid unnecessary call to plant.config_virtuals()
                return
            self.defer_configure_virtuals = True
            for slot_name, sensor in str_map.items():
                sensor = self.get_raw_sensor(sensor, raise_if_not_found=True)
                self.map_sensor(sensor=sensor, slot_name=slot_name)
                # elif sensor is None and slot_name in self.sensor_map:
                #     del self.sensor_map[slot_name]

            self.defer_configure_virtuals = False
            if self.plant is not None:
                self.plant.config_virtuals()
        else:
            raise ConfigurationError(f"sensor_map must be in the form {'slot_name:sensor_raw_name'}, got {str_map}.")

    def get_raw_sensor(self, str_map, raise_if_not_found=False):
        if str_map is None:
            return None
        return self.plant.get_raw_sensor(str_map, raise_if_not_found)

    # 2022-10-11 Currenly this method is not in use. If re-activated, also uncomment the tests in get_display_name
    # def get_display_name(self, slot_name: str, fmt: str = 'dru'):
    #     """Return display name in different formats, based on Sensor and SensorMap information.
    #     """
    #     if slot_name not in self.sensors:
    #         return None
    #     sensor = self.sensors[slot_name]
    #     map = self.sensor_map[slot_name]
    #     raw = sensor.raw_name.split('___virtual')[0] if sensor.is_virtual else sensor.raw_name
    #     raw = '(' + raw + ')'
    #     descriptive = map.descriptive_name
    #     # pint string formatting: https://pint.readthedocs.io/en/0.10.1/tutorial.html#string-formatting
    #     # unit = None if sensor.native_unit is None else f"{sensor.native_unit:~H}"
    #     unit = 'None' if sensor.native_unit is None else f"{sensor.native_unit:~P}"
    #     unit = '[' + unit + ']'
    #
    #     if fmt in ['r', 'raw']:
    #         return raw
    #     if fmt in ['d', 'descriptive']:
    #         return descriptive
    #     if fmt in ['u', 'unit']:
    #         return unit
    #     if fmt == 'ru':
    #         return f"{raw} {unit}"
    #     if fmt == 'du':
    #         return f"{descriptive} {unit}"
    #     if fmt == 'rd':
    #         return f"{raw} {descriptive}"
    #     if fmt == 'dr':
    #         return f"{descriptive} {raw}"
    #     if fmt == 'dru':
    #         return f"{descriptive} {raw} {unit}"
    #     if fmt == 'dur':
    #         return f"{descriptive} {unit} {raw}"
    #     raise NotImplementedError(f'Format {fmt} not implemented.')

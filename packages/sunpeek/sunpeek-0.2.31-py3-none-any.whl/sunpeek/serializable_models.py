import datetime
import uuid
import numpy as np
from pydantic import validator, constr
from typing import Union, Dict, List
import pint.errors

import sunpeek.components as cmp
import sunpeek.components.helpers
from sunpeek.components.base import IsVirtual
from sunpeek.components.helpers import SensorMap
from sunpeek.base_model import BaseModel
from sunpeek.common.unit_uncertainty import Q

#Needed to allow con
from sunpeek.components.types import SensorType
from sunpeek.components.base import SensorSlot
from sunpeek.common.data_uploader import DataUploadResponse, DataUploadResponseFile

class ComponentBase(BaseModel):
    sensor_map: Union[Dict[str, Union[str, None]], None]

    @validator('sensor_map', pre=True)
    def get_raw_name(cls, v):
        out = {}
        for key, item in v.items():
            if isinstance(item, SensorMap):
                out[key] = item.sensor.raw_name
            else:
                out[key] = item
        return out


def np_to_list(val):
    if isinstance(val, np.ndarray) and val.ndim == 1:
        return list(val)
    elif isinstance(val, np.ndarray) and val.ndim > 1:
        out = []
        for array in list(val):
            out.append(np_to_list(array))
        return out
    return val


class Quantity(BaseModel):
    magnitude: Union[float, List[float], List[List[float]]]
    units: str

    @validator('magnitude', pre=True)
    def convert_numpy(cls, val):
        return np_to_list(val)

    @validator('units', pre=True)
    def pretty_unit(cls, val):
        if isinstance(val, pint.Unit):
            return f"{val:~P}"
        return val


class SensorTypeValidator(BaseModel):
    name: str
    compatible_unit_str: str
    description: Union[str, None]
    # min_limit: Union[Quantity, None]
    # max_limit: Union[Quantity, None]
    # # non_neg: bool
    # max_fill_period: Union[datetime.timedelta, None]
    # sensor_hangs_period: Union[datetime.timedelta, None]
    # # high_maxerr_const: Union[Quantity, None]
    # # high_maxerr_perc: Union[Quantity, None]
    # # medium_maxerr_const: Union[Quantity, None]
    # # medium_maxerr_perc: Union[Quantity, None]
    # # low_maxerr_const: Union[Quantity, None]
    # # low_maxerr_perc: Union[Quantity, None]
    # # standard_install_maxerr_const: Union[Quantity, None]
    # # standard_install_maxerr_perc: Union[Quantity, None]
    # # poor_install_maxerr_const: Union[Quantity, None]
    # # poor_install_maxerr_perc: Union[Quantity, None]
    info_checks: Union[dict, None]
    max_fill_period: Union[datetime.timedelta, None]
    sensor_hangs_period: Union[datetime.timedelta, None]
    lower_replace_min: Union[Quantity, None]
    lower_replace_max: Union[Quantity, None]
    lower_replace_value: Union[Quantity, None]
    upper_replace_min: Union[Quantity, None]
    upper_replace_max: Union[Quantity, None]
    upper_replace_value: Union[Quantity, None]
    equation: Union[str, None]
    common_units: Union[list, None]


class IAM_Method(BaseModel):
    method_type: str


class IAM_ASHRAE(IAM_Method):
    method_type = 'ASHRAE'
    b: Quantity


class IAM_K50(IAM_Method):
    method_type = 'K50'
    k50: Quantity


class IAM_Ambrosetti(IAM_Method):
    method_type = 'Ambrosetti'
    kappa: Quantity


class IAM_Interpolated(IAM_Method):
    method_type = 'Interpolated'
    aoi_reference: Quantity
    iam_reference: Quantity


class CollectorTypeBase(BaseModel):
    test_reference_area: str
    test_type: str
    gross_length: Quantity
    iam_method: Union[IAM_ASHRAE, IAM_K50, IAM_Ambrosetti, IAM_Interpolated, None]
    name: str
    manufacturer_name: Union[str, None]
    product_name: Union[str, None]
    test_report_id: Union[str, None]
    licence_number: Union[str, None]
    certificate_date_issued: Union[str, datetime.datetime, None]
    certificate_lab: Union[str, None]
    certificate_details: Union[str, None]
    area_gr: Union[Quantity, None]
    area_ap: Union[Quantity, None]
    gross_width: Union[Quantity, None]
    gross_height: Union[Quantity, None]
    a1: Union[Quantity, None]
    a2: Union[Quantity, None]
    a5: Union[Quantity, None]
    kd: Union[Quantity, None]
    eta0b: Union[Quantity, None]
    eta0hem: Union[Quantity, None]
    f_prime: Union[Quantity, None]


class CollectorType(CollectorTypeBase):
    id: int
    b0: Union[Quantity, None]
    kb_50: Union[Quantity, None]
    khem_50: Union[Quantity, None]


class CollectorTypeQDT(CollectorTypeBase):
    a1: Quantity
    a2: Quantity
    a5: Quantity


class CollectorTypeSST(CollectorTypeBase):
    ceff: Quantity


class SensorBase(BaseModel):
    description: Union[str, None]
    accuracy_class: Union[sunpeek.components.helpers.AccuracyClass, None]
    installation_condition: Union[sunpeek.components.helpers.InstallCondition, None]
    info: Union[dict, None] = {}
    raw_name: Union[str, None]
    native_unit: Union[str, None]

    @validator('info', pre=True)
    def convert_info(cls, v):
        if isinstance(v, cmp.SensorInfo):
            return v._info
        return v

    @validator('native_unit', pre=True)
    def check_unit(cls, v):
        if isinstance(v, str):
            Q(1, v)

        return v


class Sensor(SensorBase):
    id: Union[int, None]
    plant_id: Union[int, None]
    raw_name: Union[str, None]
    sensor_type: Union[str, None]
    native_unit: Union[str, None]
    is_virtual: Union[bool, None]
    can_calculate: Union[bool, None]
    is_mapped: Union[bool, None]

    @validator('sensor_type', pre=True)
    def convert_sensor_type(cls, v):
        if isinstance(v, cmp.SensorType):
            return v.name
        return v

class NewSensor(SensorBase):
    raw_name: str
    native_unit: str = None


class BulkUpdateSensor(Sensor):
    id: int


class FluidDefintion(SensorBase):
    id: Union[int, None]
    model_type: str
    name: str
    manufacturer: Union[str, None]
    description: Union[str, None]
    is_pure: bool
    dm_model_sha1: Union[str, None]
    hc_model_sha1: Union[str, None]
    heat_capacity_unit_te: Union[str, None]
    heat_capacity_unit_out: Union[str, None]
    heat_capacity_unit_c: Union[str, None]
    density_unit_te: Union[str, None]
    density_unit_out: Union[str, None]
    density_unit_c: Union[str, None]
    heat_capacity_onnx: Union[str, None]
    density_onnx: Union[str, None]

    @validator('heat_capacity_onnx', 'density_onnx', pre=True)
    def onnx_to_str(cls, v):
        try:
            return v.hex()
        except AttributeError:
            return v


class Fluid(BaseModel):
    id: Union[int, None]
    name: Union[str, None]
    manufacturer_name: Union[str, None]
    product_name: Union[str, None]
    fluid: FluidDefintion
    concentration: Union[Quantity, None]


class FluidSummary(BaseModel):
    name: Union[str, None]
    fluid: str
    concentration: Union[Quantity, None]

    @validator('fluid', pre=True)
    def fluid_name(cls, v):
        try:
            return v.name
        except AttributeError:
            return v


# class ArrayBase(BaseModel):
class Array(ComponentBase):
    id: Union[int, None]
    plant_id: Union[int, None]
    name: Union[str, None]
    collector_type: Union[str, None]
    area_gr: Union[Quantity, None]
    area_ap: Union[Quantity, None]
    azim: Union[Quantity, None]
    tilt: Union[Quantity, None]
    row_spacing: Union[Quantity, None]
    n_rows: Union[Quantity, None]
    ground_tilt: Union[Quantity, None]
    mounting_level: Union[Quantity, None]
    fluidvol_total: Union[Quantity, None]
    rho_ground: Union[Quantity, None]
    rho_colbackside: Union[Quantity, None]
    rho_colsurface: Union[Quantity, None]
    max_aoi_shadow: Union[Quantity, None]
    min_elevation_shadow: Union[Quantity, None]

    @validator('collector_type', pre=True)
    def convert_col_type(cls, v):
        if isinstance(v, cmp.CollectorType):
            return v.name
        return v


class NewArray(Array):
    name: str
    collector_type: str
    sensors: Union[Dict[str, NewSensor], None]
    sensor_map: Union[dict, None]


class PlantBase(ComponentBase):
    owner: Union[str, None]
    operator: Union[str, None]
    description: Union[str, None]
    location_name: Union[str, None]
    altitude: Union[Quantity, None]
    fluid_solar: Union[FluidSummary, str, None]
    arrays: Union[List[Array], None]
    fluid_vol: Union[Quantity, None]
    raw_sensors: Union[List[Sensor], None]

    @validator('fluid_solar', pre=True)
    def convert_fluid(cls, v):
        if isinstance(v, cmp.Fluid):
            return FluidSummary(name=v.name, fluid=v.fluid.name, concentration=getattr(v, 'concentration', None))
        return v


class Plant(PlantBase):
    name: Union[str, None]
    id: Union[int, None]
    latitude: Union[Quantity, None]
    longitude: Union[Quantity, None]
    fluid_solar: Union[FluidSummary, str, None]
    local_tz_string_with_DST: Union[str, None]


class UpdatePlant(Plant):
    sensors: Union[Dict[str, NewSensor], None]
    fluid_solar: Union[FluidSummary, None]


class NewPlant(PlantBase):
    name: str
    latitude: Quantity
    longitude: Quantity
    fluid_solar: Union[FluidSummary, None]
    raw_sensors: Union[List[NewSensor], None]
    sensor_map: Union[dict, None]


class PlantSummaryBase(BaseModel):
    name: Union[str, None]
    owner: Union[str, None]
    operator: Union[str, None]
    description: Union[str, None]
    location_name: Union[str, None]
    latitude: Union[Quantity, None]
    longitude: Union[Quantity, None]
    altitude: Union[Quantity, None]


class PlantSummary(PlantSummaryBase):
    id: int
    name: str


class Error(BaseModel):
    error: str
    message: str
    detail: str


class Job(BaseModel):
    id: uuid.UUID
    status: cmp.helpers.ResultStatus
    result_url: Union[str, None]
    plant: Union[str, None]

    @validator('plant', pre=True)
    def plant_to_str(cls, v):
        if v is not None:
            return v.name


class JobReference(BaseModel):
    job_id: uuid.UUID
    href: str

    @validator('job_id')
    def uuid_to_str(cls, v):
        if v is not None:
            return str(v)


class ConfigExport(BaseModel):
    collectors: List[CollectorType]
    sensor_types: List[SensorTypeValidator]
    fluid_definitions: List[FluidDefintion]
    plant: Plant


class SensorSlotValidator(BaseModel):
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
    sensor_type: Union[str, SensorTypeValidator]
    descriptive_name: constr(max_length=57)
    virtual: IsVirtual
    description: Union[str, None]

    # def __init__(self,
    #              name: str,
    #              sensor_type: str,
    #              descriptive_name: str,
    #              virtual: Union[IsVirtual, str],
    #              description: str = None):
    #     super().__init__(name=name, sensor_type=sensor_type, descriptive_name=descriptive_name, virtual=virtual,
    #                      description=description)


class PCMethodOutputArray(BaseModel):
    id: Union[int, None]
    array: Array
    tp_sp_measured: Union[Quantity, None]
    tp_sp_estimated: Union[Quantity, None]
    tp_sp_estimated_safety: Union[Quantity, None]
    mean_tp_sp_measured: Union[Quantity, None]
    mean_tp_sp_estimated: Union[Quantity, None]
    mean_tp_sp_estimated_safety: Union[Quantity, None]


class PCMethodOutput(BaseModel):
    id: Union[int, None]
    plant: PlantSummary

    datetime_eval_start: datetime.datetime
    datetime_eval_end: datetime.datetime

    # Algorithm settings
    pc_method_name: str
    evaluation_mode: str
    equation: int
    check_accuracy_level: int

    interval_length: Union[datetime.timedelta, None]
    wind_used: bool
    safety_combined: Union[float, None]
    safety_pipes: Union[float, None]
    safety_others: Union[float, None]
    safety_uncertainty: Union[float, None]

    max_nan_density: Union[float, None]
    min_data_in_interval: Union[int, None]
    max_gap_in_interval: Union[datetime.timedelta, None]

    # Results
    n_intervals: Union[int, None]

    datetime_intervals_start: Union[List[datetime.datetime], None]
    datetime_intervals_end: Union[List[datetime.datetime], None]

    # Plant results
    tp_measured: Union[Quantity,None]
    tp_sp_measured: Union[Quantity, None]
    tp_sp_estimated: Union[Quantity, None]
    tp_sp_estimated_safety: Union[Quantity, None]
    mean_tp_sp_measured: Union[Quantity, None]
    mean_tp_sp_estimated: Union[Quantity, None]
    mean_tp_sp_estimated_safety: Union[Quantity, None]

    target_actual_slope: Union[Quantity, None]
    target_actual_slope_safety: Union[Quantity, None]

    # Array results
    array_results: List[PCMethodOutputArray]

    fluid_solar: Union[FluidSummary, None]
    mean_temperature: Union[Quantity, None]
    mean_fluid_density: Union[Quantity, None]
    mean_fluid_heat_capacity: Union[Quantity, None]

    @validator('datetime_intervals_start', 'datetime_intervals_end', pre=True)
    def array_to_list(cls, val):
        if isinstance(val, np.ndarray):
            return list(val)


class OperationalEvent(BaseModel):
    id: Union[int, None]
    plant: Union[str, PlantSummary]
    event_start: datetime.datetime
    event_end: Union[datetime.datetime, None]
    ignored_range: bool = False
    description: Union[str, None]
    original_timezone: Union[str, None]
            
# def dataclass_to_pydantic(cls: dataclasses.dataclass, name: str) -> BaseModel:
#     # get attribute names and types from dataclass into pydantic format
#     pydantic_field_kwargs = dict()
#     for _field in dataclasses.fields(cls):
#         # check is field has default value
#         if isinstance(_field.default, dataclasses._MISSING_TYPE):
#             # no default
#             default = ...
#         else:
#             default = _field.default
#
#         try:
#             for i, typ in enumerate(_field.type.__args__):
#
#         except AttributeError:
#             pass
#
#         pydantic_field_kwargs[ _field.name] = (_field.type, default)
#
#     return pydantic.create_model(name, **pydantic_field_kwargs, __base__=BaseModel)

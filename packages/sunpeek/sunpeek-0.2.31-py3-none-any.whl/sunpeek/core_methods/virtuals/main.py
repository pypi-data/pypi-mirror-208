"""
Module implementing functionality needed for virtual sensor calculation.

Contains functions to calculate virtual sensors. Main calculation methods start with "get_()"
Includes functions to verify / assert calculation inputs.

All get_() methods
- accept inputs (for scalars): pint.Quantity, and (for series): cmp.Sensor objects
- return unit-aware pd.Series objects (pd.Series with dtype pint[unit])

Internal functions (underscore functions) accept and return things as numeric values in appropriate units
(like radiation in W/m² etc); see docstrings for details.

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
"""

from abc import ABCMeta, abstractmethod
from typing import Union
import time
import pandas as pd
import numpy as np
import scipy.signal
import pvlib as pv

import sunpeek.common.unit_uncertainty as uu
from sunpeek.common.utils import to_rd, VerifyValidateMode, sp_logger
from sunpeek.common.errors import VirtualSensorCalculationError
from sunpeek.components.types import assert_valid_collector
from sunpeek.components.fluids import assert_valid_fluid
from sunpeek.core_methods.virtuals.radiation import RadiationConversionHorizontal, RadiationConversionTilted
from metpy.calc import dewpoint_from_relative_humidity


def validate_radiation_inputs(comp):
    """Checks if component has been assigned sufficient radiation data/sensors to perform radiation conversion.

    Parameters
    ----------
    comp : components.Plant or components.Array
        Plant or Array object for which radiation components will be calculated.

    Notes
    -----
    This function can be used on a Plant and also Array level.
    Sensor tilt angle and required output angles are not taken into account.
    For a brief discussion, see https://gitlab.com/sunpeek/sunpeek/-/issues/128
    Expects component to return 4 input radiations of type global, beam, diffuse and DNI from a call to
    component.get_radiation_input_slots()
    """
    input_pattern = _get_radiation_input_pattern(*comp.radiation_input_slots)

    # No inputs
    reason = ''
    if input_pattern == '0000':
        reason = 'No radiation inputs given.'
    # 1 input, but not global
    elif input_pattern in ['0100', '0010', '0001']:
        reason = 'Cannot calculate radiation components with only 1 input which is not a global radiation.'
    # Inputs beam + DNI
    elif input_pattern == '0101':
        reason = 'Cannot calculate radiation components with only beam and DNI radiations as inputs.'

    return *(reason == '', reason),


def _get_radiation_input_pattern(*args):
    """Returns input pattern as string, where 1 if input is not None, else 0.
    Example: beam and diffuse radiation given, while global and DNI are None: pattern=='0110'.
    """
    is_given = [x is not None for x in args]
    return f'{sum([x * np.power(10, 3 - i) for i, x in enumerate(is_given)]):04d}'


class VirtualsMeta(ABCMeta):
    required_attributes = []

    def __call__(self, *args, **kwargs):
        obj = super(VirtualsMeta, self).__call__(*args, **kwargs)
        for attr_name in obj.required_attributes:
            if not getattr(obj, attr_name):
                raise ValueError(f'Required attribute "{attr_name}" not set.')
        return obj


class VirtualSensorCalculation(object, metaclass=VirtualsMeta):
    required_attributes = ['component', 'n_results']

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def _core(self, *args, **kwargs):
        raise NotImplementedError

    def _do_assert(self, check_mode: VerifyValidateMode) -> Union[bool, None]:
        return True

    @property
    def none_output(self):
        out = (None,) * self.n_results
        out = out[0] if (self.n_results == 1) else out
        return out

    def calc(self, *args, **kwargs):
        if not self.validate_data():
            return self.none_output

        try:
            start_time = time.time()
            output = self._core(*args, **kwargs)
            sp_logger.debug(f"[virtuals.main] Done in {(time.time() - start_time):3.1f}s: "
                            f"{self.component.name}, algo {self.__class__.__name__}")
            return output
        except Exception as ex:
            raise VirtualSensorCalculationError(ex)

    def verify_config(self):
        try:
            self._do_assert(check_mode=VerifyValidateMode.verify)
        except AssertionError:
            return False
        return True

    def validate_data(self):
        try:
            self._do_assert(check_mode=VerifyValidateMode.validate)
        except AssertionError:
            return False
        return True


class CalcPowerFromVolumeFlow(VirtualSensorCalculation):
    """For Plants and Arrays, calculate thermal power from fluid, volume flow and inlet & outlet temperatures.
    """

    def __init__(self, component):
        self.component = component
        self.n_results = 1

    def _core(self):
        """
        Returns
        -------
        tp : pd.Series
            Calculated thermal power.
        """

        tp = self.calc_tp_from_vf_pos(fluid=self.component.plant.fluid_solar,
                                      vf=self.component.vf.data,
                                      te_in=self.component.te_in.data,
                                      te_out=self.component.te_out.data,
                                      pos=self.component.vf.info['position'].m_as(''))
        return tp

    def _do_assert(self, check_mode):
        assert_valid_fluid(self.component.plant.fluid_solar)
        self.component.assert_verify_validate(check_mode, 'vf', 'te_in', 'te_out')
        # TODO Add these when we return more granular info from vsensor verification/validation
        # assert self.component.vf.info is not None
        # assert 'position' in self.component.vf.info

    @staticmethod
    def calc_tp_from_vf_pos(fluid, vf, te_in, te_out, pos):
        """Calculates thermal power from given fluid, volume flow and inlet & outlet temperatures.

        Parameters
        ----------
        fluid : components.Fluid
        vf : pd.Series
        te_in : pd.Series
        te_out : pd.Series
        pos : float, 0 == Volume flow sensor installed close to inlet / te_in, 1 == close to outlet / te_out

        Returns
        -------
        tp : pd.Series
            Calculated thermal power

        Notes
        -----
        Position of volume flow sensor decides which temperature has to be used for density / mass flow calculation.
        """
        rho = fluid.get_density(
            te=_get_weighted_temperature(te_in, te_out, 1 - pos, pos))
        cp = fluid.get_heat_capacity(
            te=_get_weighted_temperature(te_in, te_out))

        mf = vf * rho * cp
        tp = mf * (te_out - te_in)
        return tp.pint.to('kW')


class CalcMassFlowFromPower(VirtualSensorCalculation):
    """For Plants and Arrays, calculate mass flow from fluid, thermal power and inlet & outlet temperatures.
    """

    def __init__(self, component):
        self.component = component
        self.n_results = 1

    def _core(self):
        """
        Returns
        -------
        tp : pd.Series
            Calculated mass flow.
        """
        mf = self.calc_mf_from_tp(fluid=self.component.plant.fluid_solar,
                                  tp=self.component.tp.data,
                                  te_in=self.component.te_in.data,
                                  te_out=self.component.te_out.data)
        return mf

    def _do_assert(self, check_mode):
        assert_valid_fluid(self.component.fluid_solar)
        self.component.assert_verify_validate(check_mode, 'tp', 'te_in', 'te_out')
        # TODO Add these when we return more granular info from vsensor verification/validation
        # assert self.component.vf.info is not None
        # assert 'position' in self.component.vf.info

    @staticmethod
    def calc_mf_from_tp(fluid, tp, te_in, te_out):
        """Calculates mass flow from fluid, thermal power and inlet & outlet temperatures.

        Parameters
        ----------
        fluid : components.Fluid
        tp : pd.Series
        te_in : pd.Series
        te_out : pd.Series

        Returns
        -------
        mf : pd.Series
            Calculated mass flow.
        """
        cp = fluid.get_heat_capacity(te=_get_weighted_temperature(te_in, te_out))
        mf = tp / (cp * (te_out - te_in))
        return mf.pint.to('kg s**-1')


class CalcSolarPosition(VirtualSensorCalculation):
    """Calculates solar angles (azimuth, elevation, zenith) for Plant, based on pvlib.
    """

    def __init__(self, plant):
        self.component = plant
        self.n_results = 5

    def _core(self):
        """Calculates solar angles (azimuth, elevation, zenith) for Plant, based on pvlib.
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.solarposition.get_solarposition.html

        Returns
        -------
        azimuth, zenitz, apparenzt_zenith, elevation, apparent_elevation : pd.Series
            Angles defining the solar position.
        """
        p = self.component
        longitude = p.longitude.m_as('deg')
        latitude = p.latitude.m_as("deg")
        altitude = None if (p.altitude is None) else p.altitude.m_as('m')
        te_amb = p.te_amb
        if te_amb is None:
            # returns pd.DataFrame
            sol_pos = pv.solarposition.get_solarposition(time=p.time_index,
                                                         latitude=latitude,
                                                         longitude=longitude,
                                                         altitude=altitude)
        else:
            te_amb = te_amb.data.pint.to('degC')
            # 12 degC is the pvlib default in case no ambient temperature is known
            te_amb = te_amb.fillna(12).astype('float64').to_numpy()
            sol_pos = pv.solarposition.get_solarposition(time=p.time_index,
                                                         latitude=latitude,
                                                         longitude=longitude,
                                                         altitude=altitude,
                                                         temperature=te_amb)

        return uu.to_s(sol_pos['azimuth'], 'deg'), \
            uu.to_s(sol_pos['zenith'], 'deg'), \
            uu.to_s(sol_pos['apparent_zenith'], 'deg'), \
            uu.to_s(sol_pos['elevation'], 'deg'), \
            uu.to_s(sol_pos['apparent_elevation'], 'deg')

    def _do_assert(self, check_mode):
        self.component.assert_verify_validate(check_mode, 'latitude', 'longitude')


class CalcDewPointTemperature(VirtualSensorCalculation):
    """Calculates ambient dew point temperature based on ambient temperature and ambient relative humidity of component.
    """

    def __init__(self, plant):
        self.component = plant
        self.n_results = 1

    def _core(self):
        """Calculates ambient dew point temperature based on ambient temperature and ambient relative humidity of component.

        Returns
        -------
        te_dew : pd.Series
            Calculated ambient dew point temperature as pd.Series with dtype pint.
        """
        p = self.component
        te_dew = self.calc_te_dew_from_te_rh_amb(te_amb=p.te_amb.q_as('degC'),
                                                 rh_amb=p.rh_amb.q_as(''))
        return te_dew

    def _do_assert(self, check_mode):
        self.component.assert_verify_validate(check_mode, 'te_amb', 'rh_amb')

    @staticmethod
    def calc_te_dew_from_te_rh_amb(te_amb, rh_amb):
        te_dew = dewpoint_from_relative_humidity(te_amb, rh_amb)
        te_dew = uu.to_s(te_dew, 'degC')
        return te_dew


class CalcDNIExtra(VirtualSensorCalculation):
    """Calculates extraterrestrial solar radiation.
    """
    n_results = 1

    def __init__(self, plant):
        self.component = plant

    def _core(self):
        """Calculates extraterrestrial solar radiation using pvlib function.
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.get_extra_radiation.html

        Returns
        -------
        dni_extra : pd.Series
            Extraterrestrial solar radiation in W/m².
        """
        p = self.component
        dni_extra = pv.irradiance.get_extra_radiation(p.time_index)
        return to_rd(dni_extra)


class CalcAirmass(VirtualSensorCalculation):
    """Calculates relative and absolute airmass.
    """

    def __init__(self, plant):
        self.component = plant
        self.n_results = 2

    def _core(self):
        """Calculate absolute airmass using pvlib function.
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.atmosphere.get_absolute_airmass.html
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.atmosphere.get_relative_airmass.html

        Returns
        -------
        rel_airmass : pd.Series
            Relative airmass (numeric value).
        abs_airmass : pd.Series
            Absolute, pressure-corrected airmass (numeric value).
        """
        p = self.component
        rel_airmass = pv.atmosphere.get_relative_airmass(zenith=p.sun_apparent_zenith.s_as('deg'))
        abs_airmass = pv.atmosphere.get_absolute_airmass(airmass_relative=rel_airmass)
        return rel_airmass.astype('pint[dimensionless]'), abs_airmass.astype('pint[dimensionless]')

    def _do_assert(self, check_mode):
        self.component.assert_verify_validate(check_mode, 'sun_apparent_zenith')


class CalcLinkeTurbidity(VirtualSensorCalculation):
    """Calculate Linke turbidity.
    """

    def __init__(self, plant):
        self.component = plant
        self.n_results = 1

    def _core(self):
        """Calculate Linke turbidity using pvlib, required for clearsky irradiance calculation.
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.lookup_linke_turbidity.html#pvlib.clearsky.lookup_linke_turbidity

        Returns
        -------
        linke_turbidity : pd.Series, Linke turbidity
        """
        p = self.component
        linke_turbidity = pv.clearsky.lookup_linke_turbidity(p.time_index,
                                                             p.latitude.m_as('deg'),
                                                             p.longitude.m_as('deg'))
        return uu.to_s(linke_turbidity, 'dimensionless')

    def _do_assert(self, check_mode):
        self.component.assert_verify_validate(check_mode, 'latitude', 'longitude')


class CalcClearskyRadiation(VirtualSensorCalculation):
    """Calcualte clearsky global horizontal irradiance and DNI using pvlib.
    """

    def __init__(self, plant):
        self.component = plant
        self.n_results = 2

    def _core(self):
        """Calculate clearsky global horizontal irradiance and DNI using pvlib.
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.ineichen.html#pvlib.clearsky.ineichen
        Alternative models:
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.haurwitz.html
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.simplified_solis.html

        Returns
        -------
        rd_ghi_clearsky : pd.Series
            Global horizontal clearsky radiation
        rd_dni_clearsky : pd.Series
            Clearsky DNI radiation
        """
        p = self.component
        altitude = 0 if p.altitude is None else p.altitude.m_as('m')
        clearsky = pv.clearsky.ineichen(p.sun_apparent_zenith.m_as('deg'),
                                        p.abs_airmass.m_as(''),
                                        p.linke_turbidity.m_as('dimensionless'),
                                        altitude,
                                        p.rd_dni_extra.m_as('W m**-2'))
        # TODO This generates a RuntimeWarning: divide by zero, but the results all look good. How to treat?
        return to_rd(clearsky['ghi'], clearsky['dni'])

    def _do_assert(self, check_mode):
        self.component.assert_verify_validate(check_mode,
                                              'sun_apparent_zenith', 'abs_airmass', 'linke_turbidity', 'rd_dni_extra')


class CalcHorizontalIrradiances(VirtualSensorCalculation):
    """For a component, calculate horizontal irradiance components from component radiation input slots.
    """

    def __init__(self, plant):
        self.component = plant
        self.n_results = 4

    def _core(self):
        """Calculate component horizontal irradiance components.

        Returns
        -------
        rd_ghi : pd.Series
            Global horizontal irradiance
        rd_bhi : pd.Series
            Beam horizontal irradiance
        rd_dhi : pd.Series
            Diffuse horizontal irradiance
        rd_dni : pd.Series
            DNI irradiance
        """
        p = self.component
        rc = RadiationConversionHorizontal(plant=p,
                                           in_global=p.in_global,
                                           in_beam=p.in_beam,
                                           in_diffuse=p.in_diffuse,
                                           in_dni=p.in_dni)
        rd_ghi, rd_bhi, rd_dhi, rd_dni = rc.get_irradiance_components()
        return rd_ghi, rd_bhi, rd_dhi, rd_dni

    def _do_assert(self, check_mode):
        assert validate_radiation_inputs(self.component)[0]


class CalcTiltedIrradiances(VirtualSensorCalculation):
    """For an component, calculate global, beam and diffuse irradiance from component radiation input slots.
    """

    def __init__(self, array, strategy='feedthrough'):
        self.component = array
        self.strategy = strategy
        self.n_results = 3

    def _core(self, **kwargs):
        """Calculate component tilted irradiance components.

        Returns
        -------
        rd_gti : pd.Series
            Global tilted irradiance
        rd_bti : pd.Series
            Beam tilted irradiance
        rd_dti : pd.Series
            Diffuse tilted irradiance
        """
        a = self.component
        rc = RadiationConversionTilted(array=a,
                                       strategy=self.strategy,
                                       in_global=a.in_global,
                                       in_beam=a.in_beam,
                                       in_diffuse=a.in_diffuse,
                                       in_dni=a.in_dni,
                                       **kwargs)
        gti, bti, dti = rc.get_irradiance_components()
        return gti, bti, dti

    def _do_assert(self, check_mode):
        assert self.strategy == 'feedthrough', \
            'Only "feedthrough" strategy implemented so far.'
        assert validate_radiation_inputs(self.component)[0]


# def get_poa_irradiances(component, **kwargs):
#     rc = RadiationConversionTilted(component=component, strategy='poa',
#                                    in_global=component.in_global, in_beam=component.in_beam,
#                                    in_diffuse=component.in_diffuse, in_dni=component.in_dni,
#                                    **kwargs)
#     dni, poa_diff_iso, poa_diff_circumsolar, poa_diff_horizon = rc.get_irradiance_components()
#     return dni, poa_diff_iso, poa_diff_circumsolar, poa_diff_horizon


# rd_bti_iam not needed? Currently using CalcIAM instead.
# class CalcIAMRadiation(VirtualSensorCalculation):
#     """Calculate incidence angle modifier (IAM) and IAM-corrected beam radiation for component.
#     """
#
#     def __init__(self, component):
#         self.component = component
#         self.n_results = 2
#
#     def _core(self):
#         """Calculate IAM and IAM-corrected beam radiation.
#
#         Returns
#         -------
#         iam : pd.Series
#             Incidence Angle Modifier
#         rd_bti_iam : pd.Series
#             IAM-corrected (reduced) beam irradiance on component
#         """
#         ar = self.component
#         iam = ar.collector_type.iam_method.get_iam(aoi=ar.aoi.data,
#                                                    azimuth_diff=ar.component.sun_azimuth.data - ar.azim)
#
#         try:
#             self.component.assert_verify_validate(VerifyValidateMode.validate, 'rd_bti')
#             rd_bti_iam = uu.to_numpy(iam) * self.component.rd_bti.data
#         except AssertionError:
#             rd_bti_iam = None
#
#         return iam, rd_bti_iam
#
#     def _do_assert(self, check_mode):
#         assert not isinstance(self.component.collector_type, UninitialisedCollectorType)
#         self.component.assert_verify_validate(check_mode, 'aoi', 'azim')
#         self.component.component.assert_verify_validate(check_mode, 'sun_azimuth')


class CalcIAM(VirtualSensorCalculation):
    """Calculate incidence angle modifier (IAM) for component.
    """

    def __init__(self, array):
        self.component = array
        self.n_results = 1

    def _core(self):
        """Calculate IAM.

        Returns
        -------
        iam : pd.Series
            Incidence Angle Modifier
        """
        a = self.component
        iam = a.collector_type.iam_method.get_iam(aoi=a.aoi.data,
                                                  azimuth_diff=a.plant.sun_azimuth.data - a.azim)
        return iam

    def _do_assert(self, check_mode):
        a = self.component
        assert_valid_collector(a.collector_type)
        a.assert_verify_validate(check_mode, 'aoi', 'azim')
        a.plant.assert_verify_validate(check_mode, 'sun_azimuth')


class CalcAngleOfIncidence(VirtualSensorCalculation):
    """Calculate the angle of incidence of sun on plane of component using pvlib function.
    """

    def __init__(self, array):
        self.component = array
        self.n_results = 1

    def _core(self):
        """https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.aoi.html

        Returns
        -------
        aoi : pd.Series
            Angle of incidence
        """
        a = self.component
        aoi = pv.irradiance.aoi(surface_tilt=a.tilt.m_as('deg'),
                                surface_azimuth=a.azim.m_as('deg'),
                                solar_zenith=a.plant.sun_zenith.m_as('deg'),
                                solar_azimuth=a.plant.sun_azimuth.m_as('deg'))
        return uu.to_s(aoi, 'deg')

    def _do_assert(self, check_mode):
        a = self.component
        a.plant.assert_verify_validate(check_mode, 'sun_zenith', 'sun_azimuth')
        a.assert_verify_validate(check_mode, 'tilt', 'azim')


class CalcInternalShading(VirtualSensorCalculation):
    """Calculates internal shading (row-to-row shading) related virtual sensors of a collector component.
    """

    def __init__(self, array):
        self.component = array
        self.n_results = 4

    def _core(self):
        """Calculates internal shading (row-to-row shading) and several related virtual sensors of a collector component.

        Returns
        -------
        is_shadowed : pd.Series
            bool. True if there is any (internal) shadow on the collector component. This takes into account: maximum
            angle of incidence, minimum sun elevation, no internal (row-to-row) shading.
        internal_shading_ratio : pd.Series
            Float between 0 and 1. Degree of shading of the collectors due to row-to-row shading,
            from not shaded (0) to completely shaded (1).
        shadow_angle : pd.Series
            Shadow angle between collector rows: Required minimum sun elevation in order not to have beam shading.
        shadow_angle_midpoint : pd.Series
            Shadow angle between collector rows, at half of the collector's slant height (i.e. the "midpoint"): Sun
            elevation that corresponds to an internal_shading_ratio of 0.5. This can be used as a typical angle for
            diffuse masking.

        Notes
        -----
        Calculation based on [1].

        internal_shading_ratio calculation taken from ADA implementation:
        https://gitlab.com/sunpeek/sunpeek/uploads/d383e5e42f77516953810e13ac0f42cb/vDP_CollectorField_rd_bT_shaded.m
        This implementation has been extended and takes component.ground_tilt into account.
        Not used in algorithms: component pressure, component humidity / dewpoint
        See also discussion in https://gitlab.com/sunpeek/sunpeek/-/issues/128/

        References
        ----------
        .. [1] Bany, J. and Appelbaum, J. (1987): "The effect of shading on the design of a field of solar collectors",
            Solar Cells 20, p. 201 - 228
            :doi:`https://doi.org/10.1016/0379-6787(87)90029-9`
        """
        a = self.component
        p = a.plant
        aoi_projection = pv.irradiance.aoi_projection(surface_tilt=a.tilt.m_as('deg'),
                                                      surface_azimuth=a.azim.m_as('deg'),
                                                      solar_zenith=p.sun_zenith.m_as('deg'),
                                                      solar_azimuth=p.sun_azimuth.m_as('deg'))
        sun_behind_coll = (aoi_projection < 0)
        sun_below_horizon = (a.plant.sun_elevation.m_as('deg') <= 0)

        # Formula (18), nomenclature according to BANY and APPELBAUM (1987)
        beta = a.tilt.m_as('rad') - a.ground_tilt.m_as('rad')
        sb = np.sin(beta)
        cb = np.cos(beta)

        A = a.collector_type.gross_length.m_as('m')

        Hc = A * np.sin(beta)
        D = a.row_spacing.m_as('m') - A * cb
        # Relative collector spacing:
        Drel = D / Hc
        gamma = p.sun_azimuth.m_as('rad') - a.azim.m_as('rad')
        alpha = p.sun_elevation.m_as('rad')

        # hs: shadow height [0..1]
        cg = np.cos(gamma)
        hs = 1 - ((Drel * sb + cb) / (cb + sb * cg / np.tan(alpha)))
        hs[hs > 1] = 1
        hs[hs < 0] = 0
        hs[sun_behind_coll * sun_below_horizon] = 1
        internal_shading_ratio = uu.to_s(hs, 'dimensionless')

        # From formula of hs calculate shadow angle (as minimum sun elevation: no beam shading if sun above this angle)
        alpha_min = np.arctan(cg / Drel)
        shadow_angle = uu.to_s(alpha_min, 'rad').pint.to('deg')

        # Shadow_angle_midpoint is the shadow angle at half of the collector's slant height.
        alpha_min = np.arctan(cg / (2 * Drel + cb / sb))
        shadow_angle_midpoint = uu.to_s(alpha_min, 'rad').pint.to('deg')

        # is_shadowed: tells if the component generally is to be considered as affected by shadow or not.
        is_not_shadowed = np.ones(len(shadow_angle))
        if a.max_aoi_shadow is not None:
            is_not_shadowed *= (a.aoi.m_as('deg') <= a.max_aoi_shadow.m_as('deg'))
        if a.min_elevation_shadow is not None:
            is_not_shadowed *= (p.sun_apparent_elevation.m_as('deg') >= a.min_elevation_shadow.m_as('deg'))
        is_not_shadowed *= (internal_shading_ratio == 0)
        is_shadowed = uu.to_s(1 - is_not_shadowed, 'dimensionless')

        return is_shadowed, internal_shading_ratio, shadow_angle, shadow_angle_midpoint

    def _do_assert(self, check_mode):
        a = self.component
        assert_valid_collector(a.collector_type)
        assert a.collector_type.gross_length is not None
        a.assert_verify_validate(check_mode, 'tilt', 'azim', 'row_spacing', 'aoi')
        a.plant.assert_verify_validate(check_mode, 'sun_zenith', 'sun_azimuth', 'sun_elevation')


class CalcArrayTemperatures(VirtualSensorCalculation):
    """Calculate mean operating temperature of collector component and its temperature derivative.
    """

    def __init__(self, array):
        self.component = array
        self.n_results = 2

    def _core(self):
        """Calculate mean operating temperature of collector component and its temperature derivative.

        Returns
        -------
        te_op : pd.Series
            Mean operating temperature
        te_op_deriv : pd.Series
            Derivative of mean operating temperature

        Notes
        -----
        Implementation explanation:
        `te_op` is smoothened with a Savitzky-Golay for more robust differentiation. Bad / noisy: te_op.diff()
        Mathematically, we just have (te(t_N) - t(t_0))/dt, for regularly spaced data.
        Using 'te_op_deriv' is preferred over this because instantaneous changes in `te_in` and `te_out`
        make `te_op` a bad predictor for real mean temperature.
        Integrating over a smoothened `te_op_deriv` is probably a better option, as the calculation then depends
        not only on 2 single measurements, avoiding negative effects like meas. uncertainty of single measurements,
        measurement delay and transport effects etc. So smoothing over all data should improve results.
        More research on this should be done, especially on non-regularly spaced data.
        """
        # Mean operating temperature
        a = self.component
        te_op = _get_weighted_temperature(a.te_in.data, a.te_out.data)
        te_op = pd.Series(uu.to_numpy(te_op, 'K'), index=a.plant.time_index)

        # Derivative of mean operating temperature
        mean_sampling_rate = a.plant.time_index.to_series().diff().min()
        # Filling NaNs, otherwise savgol fails. Downstream methods need to filter intervals with too many NaNs out.
        te_op.fillna(method='pad', inplace=True)
        te_op_deriv = scipy.signal.savgol_filter(te_op, mode='mirror', window_length=15, polyorder=3, deriv=1)
        te_op_deriv_final = te_op_deriv / mean_sampling_rate.total_seconds()  # now in K / s

        return uu.to_s(te_op, 'K'), uu.to_s(te_op_deriv_final, 'K s**-1')

    def _do_assert(self, check_mode):
        self.component.assert_verify_validate(check_mode, 'te_in', 'te_out')


def _get_weighted_temperature(te1, te2, w1=0.5, w2=0.5):
    """Return weighted average between temperature pd.Series te1 and te2.
    Takes care of converting things to K before doing the weighting. Result will be unit-aware pd.Series in degC.
    """
    # te_weighted = w1 * te1.pint.to('K') + w2 * te2.pint.to('K')
    # return uu.to_s(te_weighted, 'degC')
    # This greatly improves speed, especially in presence of many NaNs in data
    te_weighted = w1 * te1.pint.to('K').astype('float64') + w2 * te2.pint.to('K').astype('float64')
    return uu.to_s(te_weighted, 'K')

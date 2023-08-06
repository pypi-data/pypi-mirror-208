# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Callable
import pandas as pd

from sunpeek.common.unit_uncertainty import Q
from sunpeek.common.utils import VerifyValidateMode
from sunpeek.components.physical import Plant, Array
from sunpeek.components.types import assert_valid_collector


def create_eq(equation_id):
    if equation_id == 1:
        return Equation1()
    elif equation_id == 2:
        return Equation2()
    else:
        raise ValueError(f'Unknown "equation_id" {equation_id}.')


class Equation(ABC):
    """
    Template for the Equations as defined in the ISO DIS 241934:
    It specifies how power is estimated and what filter criteria to need to be applied.

    "
    # 5.1 Stating an estimate for the thermal power output of a collector field
    The estimated power output of the collector array is given as an equation_id depending on the collector parameters
    according to ISO 9806 and operation conditions. The measured power shall comply with the corresponding calculated
    power according to this equation_id. Measured and calculated power are nly compared under some specific conditions
    to avoid too large uncertainties - see section 5.4

    The estimate is given by stating the equation_id to be used for calculating the power output, including specific
    values for the parameters in equation_id. The three possible equations are given in the next three subsections.
    The collector module efficiency parameters eta0_hem, eta0_b, Kb(theta) Kd, a1, a2, a5 [1] and a8 should be based on
    certified test results. When an estimate is given it shall always be stated which equation_id shall be used for
    checking the performance:

    a) Simple check, using total radiation on the collector plane when checking the power output (ISO this standard,
    eq 1).
    b) Advanced check, using direct and diffuse radiation on collector plane wehn checking the power output
    (ISO this standard, eq 2).
    c) Advanced check, using only direct radiation on collector plane when checking the the power output
    (ISO this standard, eq3)

    [1] in the older Solar Keymark data sheets a5 is denoted c_eff
    "
    """

    id = None

    # Restricions on operating conditions based on Table 1 of standard ISO 24194.
    # Only data that pass these restrictions (as averages over given time range) are used for calculation of estimated
    # array power.
    # Common to equations 1 & 2
    max_deltat_collector = Q(5.0, 'K hour**-1')
    min_te_amb = Q(5.0, 'degC')
    max_wind_speed = Q(10, 'm s**-1')

    def __init__(self, ignore_wind: bool = False):
        """
        Parameters
        ----------
        ignore_wind : bool
            if True, the wind speed parameter is ignored during fining valid data records.
            Default: False
        """
        self.ignore_wind = ignore_wind
        return

    @staticmethod
    def _assert_available_common(array, check_mode):
        assert array.area_gr is not None, \
            f'Array {array}: array gross area "area_gr" is None.'

        assert_valid_collector(array.collector_type)
        for param in ['a1', 'a2', 'a5', 'eta0b', 'kd']:
            assert getattr(array.collector_type, param) is not None, \
                f'Array {array}: collector coefficient "{param}" is required to run the PC method but not available.'

        array_ok, problem_slots = array.verify_validate(check_mode, 'te_op', 'te_op_deriv', 'is_shadowed', 'iam')
        assert array_ok, \
            f"Array {array}: sensors are required to run the PC method but not available: {problem_slots}."

    @abstractmethod
    def assert_available(self,
                         array: Array,
                         verify_validate: VerifyValidateMode):
        """Asserts whether equation fulfills all requirements == can be applied to array, either in
        'verify' (config only) or in 'validate' (with data) mode.

        Parameters
        ----------
        array : Array to check
        verify_validate : str, 'verify' or 'validate' (see check_mode module docstring for details)

        Returns
        -------
        Nothing
        """
        raise NotImplementedError

    @abstractmethod
    def get_nan_mask(self, plant: Plant, ignore_wind: bool):
        """This method checks whether all sensors required to apply an equations are available.

        Returns
        -------
        bool : True where any of the sensors required to calculate equation are NaN.

        Notes
        -----
        In this PC Method implementation, only data records are used where none of the needed sensor records is NaN.
        Make sure _set_equation() has been called before, so self.equation_id is not None.
        """
        raise NotImplementedError

    @staticmethod
    def _get_nan_mask_common(plant, ignore_wind):
        """This method checks sensors common to both equations 1 and 2.
        """
        # Plant
        mask = plant.te_amb.data.isna()
        mask = mask | plant.tp.data.isna()
        mask = mask | plant.sun_apparent_elevation.data.isna()
        if not ignore_wind:
            mask = mask | plant.ve_wind.data.isna()

        # Arrays
        for array in plant.arrays:
            mask = mask | array.te_op.data.isna()
            mask = mask | array.te_op_deriv.data.isna()
            mask = mask | array.is_shadowed.data.isna()

        return mask

    @abstractmethod
    def calc_pc_restrictions(self, plant: Plant, ignore_wind: bool, resampler: Callable) -> pd.Series:
        """Check the operating condition restrictions of ISO 24194. Implements Table 1, chapter 5.4.

        Parameters
        ----------
        plant : Plant
        ignore_wind : bool
        resampler : Callable
            Aggregates single records into an aggregated value, e.g. hourly mean.

        Returns
        -------
        pd.Series : bool mask, True where any of the sensors required to calculate equation are NaN.

        Notes
        -----
        From the ISO DIS 241934:
            # 6.2 Valid data records
            Only data records (hourly average values) fulfilling the requirements in section 5.4 are valid.
            For checking the collector performance, the measuring period shall have at least 20 datapoints.
            [...]
            All valid datapoints should be used unless it is obvious that errors in the data or very atypical
            operating conditions occur (omitting valid data points shall be reported and justified).
        """
        raise NotImplementedError

    def _calc_pc_restrictions_common(self, plant, ignore_wind, resampler) -> pd.Series:
        """Checks the operating condition restrictions that are common to Equation 1 and Equation 2.

        Returns
        -------
        pd.Series : bool mask
        """
        # minimum ambient temperature
        is_valid = resampler(plant.te_amb.data) >= self.min_te_amb
        if not ignore_wind:
            # maximum wind speed
            is_valid = is_valid & (resampler(plant.ve_wind.data) <= self.max_wind_speed)

        for array in plant.arrays:
            # shading
            is_valid = is_valid & (resampler(array.is_shadowed.data, 'sum') == 0)
            # maximum temperature change
            is_valid = is_valid & (resampler(array.te_op_deriv.data).abs() <= self.max_deltat_collector)

        return is_valid

    @abstractmethod
    def calc_estimated_power(self, array: Array, aggregator: Callable) -> pd.Series:
        """Calculates the estimated specific power output of the collector based on the ISO equation_id formula.

        Parameters
        ----------
        array : Array
        aggregator : Callable
            Aggregates single records into an aggregated value, e.g. hourly mean.

        Returns
        -------
        pd.Series : Estimated power output of the collector, unit-aware series compatible to unit [W m**-2]
        """
        raise NotImplementedError


class Equation1(Equation):
    """ Implements Equation 1 of the ISO 24194. See Equation base class for more infos.
    """
    id = 1

    # Restrictions specific to equation 1
    # max_aoi = Q(30, 'deg')
    # Deliberately set maximum incidence angle (not defined in ISO 24194) to avoid numerical problems and problems
    # with calculated Kd values at high incidence angles.
    max_aoi_khem = Q(75, 'deg')
    min_rd_gti = Q(800, 'W m**-2')

    def assert_available(self, array, verify_validate):
        """Asserts whether all requirements are fulfilled to apply equation 1 to given array.
        """
        self._assert_available_common(array, verify_validate)

        assert array.collector_type.eta0hem is not None, \
            f'Array {array}: collector coefficient "eta0hem" is required to run PC method eq. 1 but not available.'

        array_ok, problem_slots = array.verify_validate(verify_validate, 'rd_gti', 'aoi')
        assert array_ok, \
            f"Array {array}: sensors are required to run PC method eq. 1 but not available: {problem_slots}."

    def get_nan_mask(self, plant: Plant, ignore_wind: bool):
        mask = self._get_nan_mask_common(plant, ignore_wind)
        for array in plant.arrays:
            mask = mask | array.rd_gti.data.isna()
            mask = mask | array.aoi.data.isna()

        return mask

    def calc_pc_restrictions(self, plant, ignore_wind, resampler) -> pd.Series:
        is_valid = self._calc_pc_restrictions_common(plant, ignore_wind, resampler)

        for array in plant.arrays:
            # Minimum diffuse radiation
            is_valid = is_valid & (resampler(array.rd_gti.data) >= self.min_rd_gti)
            # Question: Use max aoi here, or mean, or...? Fails occasionally with 'max', not sure why, see #268
            # maximum incidence angle --> This criterion got removed in version ISO 24194:2022(E).
            # is_valid = is_valid & (resampler(array.aoi.data, 'mean') <= self.max_aoi)
            # Maximum incidence angle: not included as a criterion in ISO 24194:2022(E), but necessary to ensure
            # stability  
            is_valid = is_valid & (resampler(array.aoi.data, 'mean') <= self.max_aoi_khem)

        return is_valid

    def calc_estimated_power(self, array, aggregator) -> pd.Series:
        """Calculates the estimated power output of a collector array based on equation 1 formula in ISO 24194.
        """
        # Collector coefficients
        a1 = array.collector_type.a1
        a2 = array.collector_type.a2
        a5 = array.collector_type.a5
        eta0b = array.collector_type.eta0b
        eta0hem = array.collector_type.eta0hem
        kd = array.collector_type.kd

        # Measurements
        rd_gti = aggregator(array.rd_gti.data)
        te_amb = aggregator(array.plant.te_amb.data)
        te_op = aggregator(array.te_op.data)
        te_op_deriv = aggregator(array.te_op_deriv.data)

        # Calculation of hemispheric incidence angle modifier for global tilted radiation:
        # Calculation is based on ISO 9806:2017 annex B, with variable name iam_xx used here instead of K_xx
        # G * iam_hem * eta0hem = G * eta0b * (0.85 * iam_b + 0.15 * iam_d)
        kb = aggregator(array.iam.data)
        khem = (eta0b / eta0hem) * (0.85 * kb + 0.15 * kd)

        tp_estimated_specific = eta0hem * khem * rd_gti \
                               - a1 * (te_op - te_amb) \
                               - a2 * (te_op - te_amb) ** 2 \
                               - a5 * te_op_deriv

        return tp_estimated_specific.astype('pint[W m**-2]')


class Equation2(Equation):
    """ Implements Equation 2 of the ISO 24194. See Equation base class for more infos.
    """

    id = 2

    # Restrictions specific to equation 1
    min_rd_bti = Q(600, 'W m**-2')

    def get_nan_mask(self, plant: Plant, ignore_wind: bool):
        mask = self._get_nan_mask_common(plant, ignore_wind)
        for array in plant.arrays:
            mask = mask | array.rd_bti.data.isna()
            mask = mask | array.rd_dti.data.isna()
            mask = mask | array.iam.data.isna()

        return mask

    def assert_available(self, array, check_mode):
        """Asserts whether all requirements are fulfilled to apply equation 2 to given array.
        """
        self._assert_available_common(array, check_mode)

        array_ok, problem_slots = array.verify_validate(check_mode, 'rd_bti', 'rd_dti')
        assert array_ok, \
            f"Array {array}: sensors are required to run PC method eq. 2 but not available: {problem_slots}."

    def calc_pc_restrictions(self, plant, ignore_wind, resampler) -> pd.Series:
        is_valid = self._calc_pc_restrictions_common(plant, ignore_wind, resampler)

        for array in plant.arrays:
            # Minimum beam radiation
            is_valid = is_valid & (resampler(array.rd_bti.data) >= self.min_rd_bti)

        return is_valid

    def calc_estimated_power(self, array, aggregator) -> pd.Series:
        """Calculates the estimated specific power output of a collector array based on equation 2 formula in ISO 24194.
        """
        # Collector coefficients
        a1 = array.collector_type.a1
        a2 = array.collector_type.a2
        a5 = array.collector_type.a5
        eta0b = array.collector_type.eta0b
        kd = array.collector_type.kd

        # Measurements
        rd_bti = aggregator(array.rd_bti.data)
        rd_dti = aggregator(array.rd_dti.data)
        iam_b = aggregator(array.iam.data)
        te_amb = aggregator(array.plant.te_amb.data)
        te_op = aggregator(array.te_op.data)
        te_op_deriv = aggregator(array.te_op_deriv.data)

        tp_estimated_specific = eta0b * iam_b * rd_bti + eta0b * kd * rd_dti \
                               - a1 * (te_op - te_amb) \
                               - a2 * (te_op - te_amb) ** 2 \
                               - a5 * te_op_deriv

        return tp_estimated_specific.astype('pint[W m**-2]')

"""
Implements Performance Check (PC) Method according to technical standard ISO/DIS 24194.

HowTo
=====

To create instances, use
- PCMethod.create_iso()
- PCMethod.create_extended()

Main method to run an analysis is pc_method.run()
Results: pc_method.get_results() returns a components.results.PCMethodOutput object.

See docstring in __init__ for more details.

Implementations
===============
PCMethodISO
-----------

The implementation variant that aligns as closely as possible to the ISO 24194 standard is in class PCMethodISO.
Create an analysis with PCMethod.create_iso(**kwargs).

PCMethodExtended
----------------

Reasoning: Some of the data analysis recommendations described in the ISO standard apprently assume the use of Excel or
other spreadsheet based software. For instance, analysis is based on fixed 1-hourly that start at full hours. This
does not necessarily lead to the best / most useful results.

This software package implements a variant of the PC method that overcomes some limitations of the strictly ISO-based
variant. It has a few slight but significant improvements in data analysis and offers some more flexibility,
while sticking as closely as possible to the intentions and purpose of the ISO 24194 standard.

First analysis validations on real-plant data confirmed that the PCMethodExtended variant reduces
noise in the analysis output and improves the regression between measured and estimated power, the main KPI of the PC
method.

Differences of PCMethodExtended over PCMethodISO in detail:
- Uses rolling resampling instead of fixed-hour resampling in PCMethodISO. Consequently, data intervals used for the
analysis (performance equations) are not restricted to start at full hours.
- Uses a minimum-noise (minimum relative standard deviation) criterion to select among overlapping interval candidates.
- Allows different interval lengths, not restricted to 1 hour.
- Minimum number of non-NaN data records per interval not restricted to 20.

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Lukas Feierl <l.feierl@solid.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
"""

from abc import ABC, abstractmethod
import warnings
import datetime as dt
import pandas as pd
import numpy as np
import numbers
from statsmodels.formula import api as smf

from sunpeek.common.unit_uncertainty import Q
from sunpeek.common.errors import ConfigurationError
from sunpeek.components import Plant, PCMethodOutput, PCMethodOutputArray
from sunpeek.core_methods.pc_method import equation as eq
from sunpeek.common.errors import PCMethodError
from sunpeek.core_methods.pc_method.verify_validate import AvailablePCEquations, AvailablePCMethods
from sunpeek.common.utils import sp_logger

# Default Parameter for PC Method
INTERVAL_LENGTH_ISO = dt.timedelta(hours=1)  # 1 hour = specified in ISO standard
F_PIPES = 0.98
F_UNCERTAINTY = 0.90
F_OTHERS_EQ1 = 0.98
F_OTHERS_EQ2 = 0.99
MIN_DATA_IN_INTERVAL = 10
MAX_GAP_IN_INTERVAL = dt.timedelta(minutes=30)
MAX_NAN_DENSITY = 0.05  # maximum allowed NaN share per interval (0 = no NaNs allowed, 1 = all NaNs is ok)
MIN_INTERVALS_IN_OUTPUT = 20


class PCMethod(ABC):
    """Superclass for various variants of the Performance Check Method.

    Parameters
    ----------
    plant : Plant
        Fully-configured plant with at least one array, and with virtual sensors calculated.
    equation_id : {1, 2} (optional)
        equation_id to be used for the pc method. If 'None', equation_id is chosen based on the input data.
        Default: None
    ignore_wind : bool (optional)
        if True, the wind speed sensor is ignored as a restriction to finding valid intervals for the PC method.
        Automatically set to True if plant has no wind measurement (plant.ve_wind is None).
        Default: False

    safety_pipes : float (optional)
        Safety factor considering heat losses from pipes etc. in the collector loop. To be estimated based on an
        evaluation of the pipe losses - normally only a few %.
        Default: None (0.98)
    safety_uncertainty : float (optional)
        Safety factor considering measurement uncertainty. To be estimated - with the requirements given in 6.1,
        a factor of 0.9 - 0.95 could be recommended depending on accuracy level.
        Default: None (will be set according to plant_measurement_accuracy)
    safety_others: float (optional)
        Safety factor for other uncertainties e.g. related to non-ideal conditions such as: • non-ideal flow
        distribution. To be estimated - should be close to one. • unforeseen heat losses. To be estimated - should
        be close to one. • uncertainties in the model/procedure itself. To be estimated - should be close to one.
        Note - it is recommended to put fO ≤ 1 when eq. (1) is used, as eq. (1) does not consider the influence of
        incidence angle modifiers.
        Default: None (will be set according to used equation)

    check_accuracy_level : {1, 2} (optional)
        Level of accuracy of sensor as specified in ISO chapter 6. Will only be used for reporting and does not
        influence the output of the pc method.
    interval_length : dt.datetime (optional)
        Length of the interval over which single data records are averaged.
        This is set to 1 hour in the ISO 24194 standard, but can be changed for PCMethodExtended.

    max_nan_density : float (optional)
        maximum percentage of missing data allowed. Intervals which have higher nan density will be discarded.
    min_data_in_interval : int (optional)
        Minimum non-NaN values per interval (defined by self.interval_length).
        The default value of 20 is stated in ISO 24194 chapter 6.2.
        Explanation: Independently from NaNs, the situation could arise where there are only a few values in an
        interval, and it doesn't make much sense to include such intervals.
    max_gap_in_interval : dt.timedelta
        Even if an interval has a minimum number of intervals (at least min_data_in_interval), those records might be
        clustered e.g. at the beginning or end of the interval, with large gaps without data records in between.
    """

    method_name = ""
    mode = ""

    def __init__(self,
                 plant: Plant,
                 equation_id: int = None,
                 ignore_wind: bool = False,
                 safety_pipes: float = None,
                 safety_uncertainty: float = None,
                 safety_others: float = None,
                 check_accuracy_level: int = 2,
                 interval_length: dt.timedelta = INTERVAL_LENGTH_ISO,
                 min_data_in_interval: int = MIN_DATA_IN_INTERVAL,
                 max_gap_in_interval: dt.timedelta = MAX_GAP_IN_INTERVAL,
                 max_nan_density: float = MAX_NAN_DENSITY,
                 ):
        self.plant = plant
        self.equation_id_in = equation_id
        self.equation = None
        self.check_accuracy_level = check_accuracy_level
        self.ignore_wind = self._set_ignore_wind(ignore_wind)

        # Safety factors
        safety_ok = lambda f: (f is None) or ((f > 0) and (f <= 1))
        for f in [safety_pipes, safety_uncertainty, safety_others]:
            if not safety_ok(f):
                raise PCMethodError(
                    'All Performance Check safety factors must be either None or floats between 0 and 1.')
        self._safety_pipes = safety_pipes
        self._safety_others = safety_others
        self._safety_uncertainty = safety_uncertainty

        self._interval_length = None
        self.max_gap_in_interval = max_gap_in_interval
        self.interval_length = interval_length
        self.min_data_in_interval = min_data_in_interval
        self.max_nan_density = max_nan_density

        self._mask = None
        self._bins = None
        self._output = {}
        return

    @classmethod
    def create(cls, method: str, plant: Plant, **kwargs):
        method = method.lower()
        if method not in list(AvailablePCMethods):
            raise PCMethodError(f"Unknown Performance Check method: {method}. "
                                f"Valid choices: {', '.join(AvailablePCMethods)}")
        if method == AvailablePCMethods.iso:
            return PCMethodISO(plant, **kwargs)
        if method == AvailablePCMethods.extended:
            return PCMethodExtended(plant, **kwargs)

    @classmethod
    def create_iso(cls, plant, **kwargs):
        return PCMethodISO(plant, **kwargs)

    @classmethod
    def create_extended(cls, plant, **kwargs):
        return PCMethodExtended(plant, **kwargs)

    @property
    def interval_length(self):
        return self._interval_length

    @interval_length.setter
    def interval_length(self, val: dt.timedelta):
        self._set_interval_length(val)

    @abstractmethod
    def _set_interval_length(self, val: dt.timedelta):
        raise NotImplementedError

    @property
    def min_data_in_interval(self):
        return self._min_data_in_interval

    @min_data_in_interval.setter
    def min_data_in_interval(self, val: int):
        if val is None:
            self._min_data_in_interval = MIN_DATA_IN_INTERVAL
            return
        assert val >= 5, \
            'Setting PC method "min_data_in_interval" to less than 5 most likely yields poor results.'
        self._min_data_in_interval = val

    @property
    def max_gap_in_interval(self):
        return self._max_gap_in_interval

    @max_gap_in_interval.setter
    def max_gap_in_interval(self, val: dt.timedelta):
        if val is None:
            self._max_gap_in_interval = 0.5 * self.interval_length
            return
        if self.interval_length is not None:
            assert val < self.interval_length, \
                f'Value of "max_gap_in_interval" ({val}) cannot be longer than interval_length {self.interval_length}.'
        self._max_gap_in_interval = val

    @property
    def max_nan_density(self):
        return self._max_nan_density

    @max_nan_density.setter
    def max_nan_density(self, val):
        if val is None:
            # Default value if not specified
            self._max_nan_density = MAX_NAN_DENSITY
        else:
            if (val >= 0) and (val <= 1):
                self._max_nan_density = val
            else:
                raise PCMethodError(
                    f'Performance Check "nan density" must be either None or a float value between 0 and 1, '
                    f'but was {str(val)}.')

    @property
    def equation_id_in(self):
        return self._equation_id_in

    @equation_id_in.setter
    def equation_id_in(self, val):
        if val is not None:
            assert isinstance(val, numbers.Number) and (val in list(AvailablePCEquations)), \
                f'Invalid PC method parameter "equation_id": {val}. Valid inputs are: ' \
                f'{", ".join([str(x.value) for x in AvailablePCEquations])}.'
        self._equation_id_in = val

    @property
    def equation_id(self):
        return None if (self.equation is None) else self.equation.id

    def _set_ignore_wind(self, user__ignore_wind):
        """Determine if wind should be ignored, depending on user input and if wind sensor is available in plant.
        """
        wind_available = (self.plant.ve_wind is not None)
        if user__ignore_wind is None:
            # ignore_wind not specified: ignore wind if sensor is not available
            return not wind_available
        else:
            if wind_available:
                return user__ignore_wind
            else:
                # Gracefully ignore wind if sensor not available
                if not user__ignore_wind:
                    sp_logger.warning(f'Performance Check overwrites input "ignore_wind" (False) and sets it to True '
                                      f'because wind sensor (plant.ve_wind) is not configured in the plant.')
                return True

    # --------------------
    # RUN related methods
    # --------------------
    @abstractmethod
    def _aggregate_candidates(self, s: pd.Series, agg_fun: str):
        """Implements the aggregation of sensor data records, e.g. hourly mean (ISO) or rolling mean (extended),
        into candidate intervals that may be selected as the final PC method intervals.

        Parameters
        ----------
        s : pd. Series
        agg_fun : str, passed to pandas aggregate

        Returns
        -------
        pd.Series : resampled data
        """
        raise NotImplementedError

    def _aggregate_intervals(self, s: pd.Series):
        """Implements the aggregation of sensor data records for the final intervals selected among the candidates.

        Parameters
        ----------
        s : pd. Series

        Returns
        -------
        pd.Series : resampled data

        Notes
        -----
        - The final intervals meet data quality requirements and the restrictions of PC method Table 1.
        - The number of intervals is usually much smaller than the number of candidates. Thus groupby should be
        faster than resampling / rolling again and then filtering on self._mask['best_intervals']
        - The same aggregation is used for PCMethodISO and PCMethodExtended.
        """
        return s.groupby(self._bins).mean()

    @abstractmethod
    def _select_best_intervals(self):
        """Among all possible intervals, select the best non-overlapping intervals to be evaluated with the PC method.
        Returns pd.Series (with index self.plant.time_index) which is True at the starting points of the intervals.
        """
        raise NotImplementedError

    def _filter_intervals(self):
        """Constructs a DataFrame with a bool column ("mask") for each criteria the data in each interval must meet.
        This bool mask is stored in self._mask

        Returns
        -------
        bool : True if at least 1 interval has been found as a result of the filtering.

        Notes
        -----
        The resulting DataFrame is stored in self._mask
        One criterion is meeting the restrictions of PC method according to ISO 24194 Tabe 1.
        Criteria that are data quality related:
        - min_data_in_interval
        - max_gap_in_interval
        - max_nan_density
        - DataFrame index is self.plant.time_index.
        """
        self._mask = pd.DataFrame()

        # min_data_in_interval
        value_count = self._aggregate_candidates(self.plant.time_index.to_series(), 'count')
        self._mask['min_data_ok'] = (value_count >= self.min_data_in_interval)

        # max_nan_density
        # nan_mask: True where _any_ of the sensors used in the PC method is NaN. Those records are rejected.
        nan_mask = self.equation.get_nan_mask(self.plant, self.ignore_wind)
        nan_density = self._aggregate_candidates(nan_mask, 'sum') / value_count
        self._mask['nan_density_ok'] = (nan_density <= self.max_nan_density)

        # max_gap_in_interval
        # Define gap of an index as average between backward and forward gap.
        bwd = self.plant.time_index.to_series().diff().dt.total_seconds()
        fwd = bwd.shift(-1)
        gaps = pd.concat([bwd, fwd], axis=1).mean(axis=1)
        max_gap = self._aggregate_candidates(gaps, 'max')
        self._mask['max_gap_ok'] = (max_gap <= self.max_gap_in_interval.total_seconds())

        # Restrictions to interval filtering described in ISO 24194 Table 1, chapter 5.4.
        self._mask['pc_restrictions'] = \
            self.equation.calc_pc_restrictions(plant=self.plant,
                                               ignore_wind=self.ignore_wind,
                                               resampler=lambda s, fun='mean': self._aggregate_candidates(s, fun))

        self._mask['best_intervals'] = self._select_best_intervals()
        n_intervals = self._mask['best_intervals'].sum()
        self._output['n_intervals'] = n_intervals

        if n_intervals < MIN_INTERVALS_IN_OUTPUT:
            warnings.warn(
                f'PC method analysis found {n_intervals} intervals. For checking the collector performance, '
                f'the ISO 24194 standard recommends to have at least {MIN_INTERVALS_IN_OUTPUT} intervals.')
        if n_intervals == 0:
            return False

        # Out of the marked best intervals, create bins for groupby
        self._bins = pd.Series(data=np.nan, index=self.plant.time_index)
        for i, end in enumerate(self._mask.index[self._mask['best_intervals']]):
            mask = (self._bins.index > end - self.interval_length) & (self._bins.index <= end)
            self._bins.loc[mask] = i

        return True

    def run(self):
        """ Applies the Performance Check on the plant and returns the estimated and calculated power."""
        # Set equation based on given equation_id_in and make sure PC method can be applied.
        # Under the hood, _set_equation() calls verify_validate.validate_data(),
        # so we can be sure plant config and data are ok to run the PC method.
        start_time = dt.datetime.now(dt.timezone.utc)
        self._set_equation()
        # self.set_safety_factors()  # cannot be done before, depends on self.equation

        if self._filter_intervals():
            self._calc_output()

        pc_method_output = self._create_output_object(start_time)
        return pc_method_output

    def _calc_output(self):
        """Calculates estimated power for plant and all arrays, saves results in self attributes.

        Returns
        -------
        Nothing. Sets self._output_plant, self._slopes and self._output_arrays
        """
        tp_estimated = 0
        te_op_mean_area = 0
        self._output['arrays'] = {}
        aggregator = self._aggregate_intervals

        for array in self.plant.arrays:
            df = self.equation.calc_estimated_power(array, aggregator).to_frame(name='tp_sp_estimated')
            df['tp_sp_estimated_safety'] = df['tp_sp_estimated'] * self.safety_combined
            df['tp_estimated'] = df['tp_sp_estimated'] * array.area_gr
            if (not array.tp.is_virtual) or (array.tp.is_virtual and array.tp.can_calculate):
                df['tp_sp_measured'] = aggregator(array.tp.data) / array.area_gr
            # save DataFrame with array results in dict
            self._output['arrays'][array] = df
            tp_estimated += df['tp_estimated']
            te_op_mean_area += aggregator(array.te_op.data) * array.area_gr

        df = aggregator(self.plant.tp.data.astype('pint[kW]')).to_frame(name='tp_measured')
        df['tp_sp_measured'] = df['tp_measured'].astype('pint[W]') / self.plant.area_gr
        df['tp_sp_estimated'] = tp_estimated / self.plant.area_gr
        df['tp_estimated'] = tp_estimated.astype('pint[kW]')
        df['tp_sp_estimated_safety'] = df['tp_sp_estimated'] * self.safety_combined
        # area-weighted mean operating temperature over all arrays
        te_op_mean = te_op_mean_area / self.plant.area_gr
        df['te_op_mean'] = te_op_mean.astype('pint[degC]')
        self._output['plant'] = df

        # Slope between measured and estimated power, for plant
        df_slopes = self._output['plant'].loc[:, ['tp_sp_measured', 'tp_sp_estimated', 'tp_sp_estimated_safety']]
        df_slopes = df_slopes.astype('float64')

        self._output['slopes'] = {}
        fit = smf.ols('tp_sp_measured ~ tp_sp_estimated -1', data=df_slopes).fit()
        self._output['slopes']['target_actual'] = Q(fit.params.to_numpy()[0], '')

        fit = smf.ols('tp_sp_measured ~ tp_sp_estimated_safety -1', data=df_slopes).fit()
        self._output['slopes']['target_actual_safety'] = Q(fit.params.to_numpy()[0], '')

    # def set_safety_factors(self):
    #     safety_pipes = self._safety_pipes
    #     safety_uncertainty = self._safety_uncertainty
    #     safety_others = self._safety_others
    #
    #     safety_pipes = F_PIPES if (safety_pipes is None) else safety_pipes
    #     safety_uncertainty = F_UNCERTAINTY if (safety_uncertainty is None) else safety_uncertainty
    #
    #     assert self.equation_id is not None, \
    #         'Cannot determine PC method safety factor "safety_others" because equation_id is None.'
    #     if safety_others is None:
    #         if self.equation_id == 1:
    #             safety_others = F_OTHERS_EQ1
    #         elif self.equation_id == 2:
    #             safety_others = F_OTHERS_EQ2
    #
    #     self._safety_pipes_final = safety_pipes
    #     self._safety_others_final = safety_others
    #     self._safety_uncertainty_final = safety_uncertainty
    #
    #     self.safety_combined = safety_others * safety_pipes * safety_uncertainty

    @property
    def safety_pipes(self):
        return F_PIPES if (self._safety_pipes is None) else self._safety_pipes

    @property
    def safety_uncertainty(self):
        return F_UNCERTAINTY if (self._safety_uncertainty is None) else self._safety_uncertainty

    @property
    def safety_others(self):
        if self.equation_id is None:
            raise PCMethodError('Cannot determine Performance Check safety factor "safety_others" because '
                                'equation_id is None. This is an internal error and should not have happened.')
        if self._safety_others is not None:
            return self._safety_others
        if self.equation_id == AvailablePCEquations.one:
            return F_OTHERS_EQ1
        elif self.equation_id == AvailablePCEquations.two:
            return F_OTHERS_EQ2

    @property
    def safety_combined(self):
        return self.safety_others * self.safety_pipes * self.safety_uncertainty

    # --------------------
    # OUTPUT related methods
    # --------------------
    def _create_output_object(self, start_time):
        """Gather all PC method calculation outputs required for ISO 24194 Annex A1, and a few more.

        Returns
        -------
        PCMethodOutput object
        """
        out = PCMethodOutput()
        out.plant = self.plant
        out.datetime_eval_start = self.plant.context.eval_start
        out.datetime_eval_end = self.plant.context.eval_end

        # Algorithm settings
        out.pc_method_name = self.method_name
        out.evaluation_mode = self.mode
        out.equation = self.equation_id
        out.check_accuracy_level = self.check_accuracy_level

        out.interval_length = self.interval_length
        out.wind_used = not self.ignore_wind
        out.safety_combined = self.safety_combined
        out.safety_pipes = self.safety_pipes
        out.safety_others = self.safety_others
        out.safety_uncertainty = self.safety_uncertainty

        out.max_nan_density = self.max_nan_density
        out.min_data_in_interval = self.min_data_in_interval
        out.max_gap_in_interval = self.max_gap_in_interval

        # Results
        out.n_intervals = self._output['n_intervals']
        if out.n_intervals == 0:
            return out

        intervals_end = self._mask.index[self._mask['best_intervals']].to_pydatetime()
        out.datetime_intervals_start = intervals_end - self.interval_length
        out.datetime_intervals_end = intervals_end

        # Plant results
        df = self._output['plant']
        unit_tp = 'pint[kW]'
        unit_tp_sp = 'pint[W m**-2]'
        out.tp_measured = df['tp_measured'].astype(unit_tp)
        out.tp_sp_measured = df['tp_sp_measured'].astype(unit_tp_sp)
        out.tp_sp_estimated = df['tp_sp_estimated'].astype(unit_tp_sp)
        out.tp_sp_estimated_safety = df['tp_sp_estimated_safety'].astype(unit_tp_sp)
        out.mean_tp_sp_measured = out.tp_sp_measured.mean()
        out.mean_tp_sp_estimated = out.tp_sp_estimated.mean()
        out.mean_tp_sp_estimated_safety = out.tp_sp_estimated_safety.mean()

        out.target_actual_slope = self._output['slopes']['target_actual']
        out.target_actual_slope_safety = self._output['slopes']['target_actual_safety']

        # Array results
        array_results = []
        for array in self.plant.arrays:
            df = self._output['arrays'][array]
            arr_out = PCMethodOutputArray()
            arr_out.array = array
            if 'tp_sp_measured' in df.columns:
                arr_out.tp_sp_measured = df['tp_sp_measured'].astype(unit_tp_sp)
                arr_out.mean_tp_sp_measured = arr_out.tp_sp_measured.mean()
            else:
                arr_out.tp_sp_measured = None
                arr_out.mean_tp_sp_measured = None
            arr_out.tp_sp_estimated = df['tp_sp_estimated'].astype(unit_tp_sp)
            arr_out.tp_sp_estimated_safety = df['tp_sp_estimated_safety'].astype(unit_tp_sp)
            arr_out.mean_tp_sp_estimated = arr_out.tp_sp_estimated.mean()
            arr_out.mean_tp_sp_estimated_safety = arr_out.tp_sp_estimated_safety.mean()

            array_results.append(arr_out)

        out.array_results = array_results

        te = self._output['plant']['te_op_mean'].mean().to('degC')
        out.mean_temperature = te
        te_s = pd.Series(data=te.to('K').magnitude).astype('pint[K]')

        out.fluid_solar = self.plant.fluid_solar
        no_fluid = (self.plant.fluid_solar is None)
        out.mean_fluid_density = None if no_fluid else Q(self.plant.fluid_solar.get_density(te_s)[0])
        out.mean_fluid_heat_capacity = None if no_fluid else Q(self.plant.fluid_solar.get_heat_capacity(te_s)[0])

        return out

    # --------------------
    # EQUATION related methods
    # --------------------
    def _set_equation(self):
        """Returns the requested equation_id class based on the requested eq_id or the sensors available to plant.
        """
        if self.equation_id_in is None:
            self.equation = self._get_optimal_equation()
        elif self._equation_available(self.equation_id_in)[0]:
            self.equation = eq.create_eq(self.equation_id_in)
        else:
            raise ConfigurationError(
                f'Requirements to apply PC Method equation {self.equation_id_in} to the plant and its arrays '
                f'are not fulfilled. '
                f'Reason: {self._equation_available(self.equation_id_in)[1]}. '
                f'For details, run pc_method.verify_validate.validate_data() on the plant.')

    def _get_optimal_equation(self):
        """Return optimal / best equation_id based on available information in plant sensors and plant config.
        Precendence is given to Equation2 if all requirements are fulfilled.
        See: https://gitlab.com/sunpeek/sunpeek/-/issues/174
        """
        if self._equation_available(2)[0]:
            return eq.create_eq(2)
        elif self._equation_available(1)[0]:
            return eq.create_eq(1)
        else:
            raise ConfigurationError(
                f'Requirements to apply PC Method equation 1 or equation 2 to the plant and its arrays '
                f'are not fulfilled. '
                f'Reason for equation 1: {self._equation_available(1)[1]}. '
                f'Reason for equation 2: {self._equation_available(2)[1]}. '
                f'For details, run pc_method.verify_validate.validate_data() on the plant.')

    def _equation_available(self, equation_id):
        """Returns whether PC equation (1 or 2) is available (all requirements fulfilled) for plant config + data.

        Returns
        -------
        tuple : False if not available, reason
        """
        from sunpeek.core_methods.pc_method import validate_data
        try:
            validate_data(self.plant, equation_id, self.ignore_wind)
        except AssertionError as ex:
            return False, ex.__str__()
        return True, ''


class PCMethodISO(PCMethod):
    """This PC method implementation aligns as strictly as possible to the method as defined in the technical
    standard ISO/DIS 24194.
    """

    method_name = "PC Method 'ISO DIS 24194'"
    mode = 'ISO'

    def _set_interval_length(self, val: dt.timedelta):
        assert val == INTERVAL_LENGTH_ISO, \
            'For a PC Method ISO evaluation, the "interval_length" is fixed to 1 hour as defined in the ISO 24194.'
        self._interval_length = val
        # Invalid max_gap? Reset to default value
        if self.max_gap_in_interval >= self.interval_length:
            self.max_gap_in_interval = None

    def _aggregate_candidates(self, s, agg_fun):
        s = s.resample(self.interval_length, closed='right', label='right').aggregate(agg_fun)
        return s

    def _select_best_intervals(self):
        """Due to the fixed-hour resampling pattern used in the PCMethodISO data aggregation, we have no overlapping
        intervals, so all intervals that fulfill all constraints (self._mask) are ok.
        """
        return self._mask.all(axis='columns')


class PCMethodExtended(PCMethod):
    """This class implements an alternative variant of the PC method, with improvements in data analysis.
    """

    method_name = "PC Method 'ISO DIS 24194' extended"
    mode = 'extended'

    def _set_interval_length(self, val: dt.timedelta):
        assert val >= dt.timedelta(minutes=15), \
            'Setting PC method "interval_length" to less than 15 minutes most likely yields poor results.'
        self._interval_length = val
        # Invalid max_gap? Reset to default value
        if self.max_gap_in_interval >= self.interval_length:
            self.max_gap_in_interval = None

    def _aggregate_candidates(self, s, agg_fun='mean'):
        s_out = s.rolling(window=self.interval_length, closed='right').aggregate(agg_fun)
        if agg_fun not in ['sum', 'count']:
            s_out = s_out.astype(s.dtype)  # rolling drops pint dtype...
        return s_out

    def _select_best_intervals(self):
        # Intervals that fulfill all constraints so far:
        is_candidate = self._mask.all(axis='columns')

        # Criterion to find "best" interval among overlapping: smallest relative standard deviation of plant power.
        tp = self.plant.tp.data
        variation = (self._aggregate_candidates(tp, 'mean') / self._aggregate_candidates(tp, 'std')).astype('float64')
        score = 1 / variation
        score[~is_candidate] = 0

        # Iteratively add best interval and remove overlapping from candidates.
        idx = self.plant.time_index
        best_intervals_mask = pd.Series(index=idx, data=False)
        while any(is_candidate):
            # Mark best-scoring interval. Exit if score is NaN in all remaining candidates:
            if score.where(is_candidate).isna().all():
                break
            # If idxmax is not unique --> returns first occurrence of maximum
            best_idx = score.where(is_candidate).idxmax()
            best_intervals_mask.loc[best_idx] = True
            # Remove overlapping intervals (past and future) from candidates
            is_candidate.loc[(idx > best_idx - self.interval_length) & (idx < best_idx + self.interval_length)] = False

        return best_intervals_mask

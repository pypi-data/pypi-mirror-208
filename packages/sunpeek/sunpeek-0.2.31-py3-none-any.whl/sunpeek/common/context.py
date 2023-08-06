"""
This module implements data access and data handling.

The Context class implements 2 data backends: database and dataframe.
- Database is e.g. for use over WebUI, DataFrame for use as a package and for testing.
A sensor cache is implemented to speed up database access times.
- To quickly add csv data / test something, just do: plant.use_csv([file_list])

Internally, data is always stored without unit (double / float64); the correct unit (stored in sensor.native_unit)
is attached at data access.
"""

import numpy as np
import pandas as pd
import sqlalchemy.orm
import enum
import datetime
from dataclasses import dataclass

from sunpeek.common.errors import ConfigurationError, VirtualSensorCalculationError, SensorDataNotFoundError, \
    TimeZoneError, TimeIndexError
from sunpeek.common.time_zone import validate_timezone

from sunpeek.db_utils import DATETIME_COL_NAME


def import_db_ops():
    """
    Imports the db_data_operations module and raises a specific error if any of the required modules is missing.
    This is used because some functions in this module only need the db modules imported when using the database backend
    """
    try:
        import sunpeek.db_utils.db_data_operations as db_ops
        return db_ops
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Some modules that a required to work with the database backend are not installed. "
                                  "They can be installed with pip install sunpeek[db].")


def sanitize_dataframe(df: pd.DataFrame) -> (pd.DataFrame, int):
    if df is None:
        return None, 0

    df = df[~df.index.isna()]
    # Some core methods require data to be sorted (e.g. PC Method extended -> rolling operation)
    df = df.sort_index()
    # Check for duplicate indices
    index_duplicates = df.index.duplicated(keep=False)
    n_duplicates_index = index_duplicates.sum()
    df = df[~index_duplicates]

    return df, n_duplicates_index


class Context:
    class Datasources(str, enum.Enum):
        db = "db"
        database = "database"  # stored as 'db'
        df = "df"
        dataframe = "dataframe"  # stored as 'df'

    VALID_DATASOURCES = [el.name for el in Datasources]

    @dataclass
    class EvalInterval:
        start: datetime.date
        end: datetime.date

        def __post_init__(self):
            if self.start is None:
                self.start = pd.to_datetime('1970-01-01 00:00', utc=True)
            if self.end is None:
                self.end = pd.to_datetime('2200-01-01 00:00', utc=True)
            # validate start, end
            for x in (self.start, self.end):
                if not isinstance(x, datetime.date):
                    raise TypeError('Context limits expected to be of type datetime.')
                if x.tzinfo is None:
                    raise TimeZoneError(
                        "Both elements of a Context eval_interval tuple must be timezone-aware datetime objects.")
            if self.end <= self.start:
                raise ValueError('A Context eval_interval must have increasing timestamps: end must be greater than ' \
                                 'start.')

    # Cannot add plant type hint because of circular imports.

    def __init__(self, plant,
                 datasource: str = None,
                 dataframe: pd.DataFrame = None,
                 df_timezone: str = None,
                 eval_start: datetime.date = None,
                 eval_end: datetime.date = None):
        if plant is None:
            raise ConfigurationError('Context parameter "plant" must not be None.')
        self.plant = plant
        self._df = None
        self._sensor_cache = {}
        self._eval_interval = None
        self.set_eval_interval(eval_start, eval_end)
        self.session = None

        if datasource is None and dataframe is not None:
            datasource = 'df'
        self.datasource = datasource
        if self.datasource == 'df':
            self.session = None
            self.use_dataframe(dataframe, timezone=df_timezone)

        elif self.datasource == 'db':
            if dataframe is not None:
                raise ConfigurationError('You are trying to set a context datasource to "db" but also provided a '
                                         'DataFrame. This is ambiguous.')
            session = sqlalchemy.orm.object_session(plant)
            if session is None:
                raise ConfigurationError(f'Context for plant {plant.name} was initialised with datasource "db", '
                                         f'but {plant.name} object is not attached to a database session')
            self.session = session

    @classmethod
    def validate_datasource(cls, val):
        """Validates datasource string and returns either 'df' or 'db'.

        Raises
        ------
        ValueError
        """
        if (val is not None) and val.lower() not in [s.lower() for s in cls.VALID_DATASOURCES]:
            raise ValueError(f'Context.datasource must be one of {cls.VALID_DATASOURCES}.')
        val = 'df' if (val == 'dataframe') else val
        val = 'db' if (val == 'database') else val
        return val

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, val):
        raise NotImplementedError(
            'You cannot directly set the DataFrame df of a Context. Use context.use_dataframe() instead.')

    @property
    def eval_start(self):
        return self._eval_interval.start

    @property
    def eval_end(self):
        return self._eval_interval.end

    @property
    def time_index(self) -> pd.DatetimeIndex:
        self._assert_datasource_df_db()

        if DATETIME_COL_NAME in self._sensor_cache:
            return self._sensor_cache[DATETIME_COL_NAME]

        idx = None
        if self.datasource == 'df':
            idx = self.df[self.eval_start:self.eval_end].index
        elif self.datasource == 'db':
            q = self.session.query(sqlalchemy.column(DATETIME_COL_NAME)).select_from(
                sqlalchemy.table(self.plant.raw_table_name)).filter(
                sqlalchemy.column(DATETIME_COL_NAME) >= self.eval_start).filter(
                sqlalchemy.column(DATETIME_COL_NAME) <= self.eval_end).order_by(
                (sqlalchemy.column(DATETIME_COL_NAME).asc())
            )
            ds = pd.read_sql(q.statement, self.session.bind)[DATETIME_COL_NAME]
            idx = pd.DatetimeIndex(ds, tz='UTC')

        if (idx is None) or (not isinstance(idx, pd.DatetimeIndex)):
            raise TimeIndexError(f'Invalid plant.time_index. Expected pd.DatetimeIndex, got {type(idx)}.')
        if not idx.is_monotonic_increasing:
            raise TimeIndexError('Invalid plant.time_index. Index is not monotonic increasing, that is: older data '
                                 'comes after newer data. This should have been prevented by SunPeek.')

        index = idx.tz_convert(self.plant.tz_data)
        self._sensor_cache[DATETIME_COL_NAME] = index

        return index

    @property
    def datasource(self):
        return self._datasource

    @datasource.setter
    def datasource(self, val):
        self._datasource = self.validate_datasource(val)
        if self._datasource == 'db':
            self._df = None
        self._sensor_cache.clear()

    def set_eval_interval(self, eval_start=None, eval_end=None):
        eval_interval = self.EvalInterval(start=eval_start, end=eval_end)
        self._eval_interval = eval_interval

    def reset_cache(self):
        """To be called whenever something happens (outside Context) that invalidates the sensor_cache, e.g.
        editing a sensor's min or max, or adding an OperationEvent to a plant.
        """
        self._sensor_cache.clear()

    def use_dataframe(self, df: pd.DataFrame,
                      timezone: str = None,
                      drop_unneeded_columns: bool = False,
                      missing_columns: str = 'ignore'):
        """Configures Context to use the supplied dataframe as the datasource, instead of accessing the database.

        Parameters
        ----------
        df : pd.DataFrame. Must have a DateTimeIndex index.
        timezone : timezone string, example 'Europe/Berlin' or 'UTC'
        missing_columns : all real sensor columns required?
        drop_unneeded_columns : bool. If True, columns not needed according to plant.get_raw_names(True) are dropped.

        Notes
        -----
        - df must have a timezone-aware DatetimeIndex
        - Only numeric information in df is used. pint dtypes are ignored. No automatic unit conversion implemented.
        - Treatment of missing columns in df compared to expected sensor raw_names: missing_columns kwarg
        """
        assert df is not None, 'DataFrame is None.'
        df.index = validate_timezone(df.index, timezone)
        df, n_duplicates = sanitize_dataframe(df)

        # Store only numeric data.
        for (col, dtype) in zip(df.columns, df.dtypes):
            # if not np.issubdtype(dtype, np.number):
            if not pd.api.types.is_numeric_dtype(dtype):
                raise ValueError(
                    "To use a DataFarme as data source for a plant / Context, "
                    "the DataFrame must only contain numeric columns. "
                    f"Column {col} has dtype {dtype}.")
        # pint unit dtype is added at sensor.data, or plant.context.get_sensor_data()
        df = df.astype('float64', errors='raise')

        assert missing_columns in ['ignore', 'raise', 'nan'], f'Invalid "missing_columns": {missing_columns}'
        if missing_columns != 'ignore':
            cols_missing = set(self.plant.get_raw_names(include_virtuals=False)) - set(df.columns)
            if (len(cols_missing) > 0) and (missing_columns == 'raise'):
                raise ValueError(
                    f'DataFrame does not have all required columns. Columns missing: {cols_missing}.')
            if cols_missing == 'nan':
                df[cols_missing] = np.nan

        # Drop unneeded columns (not used by any Sensor in the self.plant)
        if drop_unneeded_columns:
            df = df.drop(df.columns.difference(self.plant.get_raw_names(include_virtuals=True)), axis=1)

        self.reset_cache()
        self._datasource = 'df'
        self._df = df
        # By default, use whole dataframe
        self.set_eval_interval(eval_start=df.index[0], eval_end=df.index[-1])

    def get_sensor_data(self, sensor):
        """Given a sensor and raw data Returns processed data for a given sensor. Usually called as sensor.data

        Parameters
        ----------
        sensor : Sensor

        Returns
        -------
        pandas Series, raw sensor values to which processing steps defined in self.process_data() to raw sensor values.

        Notes
        -----
        If sensor.raw_name is found in context._sensor_cache, unprocessed data is returned.
        In all other cases, context._process_data() is called.
        """
        self._assert_datasource_df_db()

        if sensor.raw_name in self._sensor_cache:
            # Note: If found in _sensor_cache, data is returned as-is, therefore no call to _process_data()
            s = self._sensor_cache[sensor.raw_name]

        else:
            # Retrieve data from datasource (df or db) and process it
            if self.datasource == 'df':
                if sensor.raw_name not in self.df.columns:
                    raise KeyError(f'Data for sensor {sensor.raw_name} was not found in the cache or the dataframe.'
                                   f' The context datasource is {self.datasource}.')
                s = self.df.loc[self.eval_start:self.eval_end, sensor.raw_name]

            elif self.datasource == 'db':
                if self.session is None:
                    raise ConnectionError("Context does not have a database session available")

                sensor_data_df = import_db_ops().get_sensor_data(
                    self.session.bind.raw_connection(),
                    sensor_names=sensor.raw_name,
                    table_name=self.plant.raw_table_name,
                    start_timestamp=str(self.eval_start), end_timestamp=str(self.eval_end))

                if sensor_data_df is None:
                    raise SensorDataNotFoundError(
                        f'Column {sensor.raw_name} not found in data table for plant {self.plant}. '
                        f'See https://docs.sunpeek.org/errors.html#sensordatanotfounderror-when-using-the-database-datastore')
                s = sensor_data_df.squeeze()

            # Attach unit, call data cleaning
            s = self._process_data__native(sensor, s)
            s = s.astype(f'pint[{sensor.native_unit}]')
            # Store processed data in cache
            self._sensor_cache[sensor.raw_name] = s

        # Convert to plant data time zone
        s = s.tz_convert(self.plant.tz_data)

        return s

    def store_data(self, sensor, data: pd.Series):
        """Stores virtual sensor calculation results in datasource.

        Parameters
        ----------
        sensor : Sensor
        data : Union[pd.Series, None]
            Virtual sensor calculation results, with dtype numeric.

        Returns
        -------
        Nothing, new data is stored in the context DataFrame self.df

        Notes
        -----
        Assumes dataframe backend for speed reason. Calling code needs to take care of storing things to database.
        """
        self._assert_datasource_df_db()

        # If a vsensor calculation was not possible (for whatever reason), Context will store an all-NaN series.
        if data is None:
            data = pd.Series(data=np.nan, index=self.time_index)
        else:
            if len(data) != len(self.time_index):
                raise VirtualSensorCalculationError(
                    'Size of virtual sensor data is incompatible with size of Plant.time_index')
            data.index = self.time_index  # TODO only necessary for db
            # pint unit is stored with sensor.native_unit and attached at context.get_sensor_data
            # TODO: calling astype twice should not be needed, but otherwise we get PandasDType, check if pint bug
            data = data.astype(float).astype(float)
            # All subsequent algorithms shall rely that everything is either a number or NaN.
            # Inf may arise in virtual sensors, e.g. due to CoolProp returning Inf.
            data[~np.isfinite(data)] = np.nan

        if self.datasource == 'df':
            self.df[sensor.raw_name] = data

        elif self.datasource == 'db':
            data.name = sensor.raw_name
            data_save_ok = import_db_ops().update_virtual_sensor_data(
                self.session.bind.raw_connection(), sensor_data=data, table=self.plant.raw_table_name)
            if not data_save_ok:
                raise ConnectionError('Failed to store virtual sensor data in database table.')

        # Populate Context sensor cache for faster data retrieval in subsequent accesses
        self._sensor_cache[sensor.raw_name] = data.astype(f'pint[{sensor.native_unit}]')

    def validate_sensors(self):
        """Data quality information about the plant's sensors (self.df), taking ignored ranges into account.

        Returns
        -------
        sensor_validation : dict
            Dictionary keys are sensor.raw_name, dictionary value is a
            DataFrame reporting data quality. Index is days, columns are total number of timestamps / data values,
            number of timestamps outside ignored ranges, NaN density outside ignored ranges.
        """
        # not_ignored: marks the relevant pieces of data. True if timestamp is not within ignored range
        not_ignored = pd.Series(True, index=self.time_index)
        for irng in self.plant.ignored_ranges:
            mask = (self.time_index >= irng.left) & (self.time_index <= irng.right)
            not_ignored.loc[mask] = False

        sensor_validation = {
            raw_name: self._create_sensor_validation(not_ignored, raw_name) for raw_name in self.df.columns}

        return sensor_validation

    def _create_sensor_validation(self, not_ignored, raw_name):
        """For a given DataFrame and sensor (raw_name), create a validation DataFrame, aggregating information by day.

        Parameters
        ----------
        not_ignored : pd.Series
        raw_name : raw name of sensor, equal to df column name

        Returns
        -------
        df : pd.DataFrame
            DataFrame index are days, columns contain:
            number of total timestamps
            number of not_ignored timestamps
            number of nans in not_ignored ranges
            nan density in not_ignored ranges
        """
        # Total number of timestamps per day
        days = self.time_index.date
        df_out = not_ignored.groupby(by=days).count().to_frame(name='n_timestamps')

        # Number of not_ignored timestamps per day
        df_out['n_timestamps_not_ignored'] = not_ignored.groupby(by=days).sum()

        # Nans in not-ignored ranges (the ones that actually hurt)
        nan_not_ignored = self.df.loc[:, raw_name].isna() & not_ignored
        df_out['n_nans_not_ignored'] = nan_not_ignored.groupby(by=days).sum()

        # Nan density in not-ignored ranges.
        df_out['nan_density_not_ignored'] = df_out['n_nans_not_ignored'] / df_out['n_timestamps_not_ignored']

        df_out.index = pd.to_datetime(df_out.index)
        return df_out

    # def _process_data(self, sensor, s_raw):
    #     """This is the main data processing method, it implements e.g. min max filtering, plant.ignored_ranges etc.
    #
    #     Parameters
    #     ----------
    #     sensor : Sensor
    #     s_raw : pd.Series
    #         Unprocessed data for sensor, with pint dtype, typically obtained from self.get_sensor_data()
    #
    #     Returns
    #     -------
    #     s : pd.Series
    #         Processed data for sensor, with pint dtype.
    #     """
    #     s = s_raw
    #     # Set values in ignored ranges to NaN
    #     for irng in self.plant.ignored_ranges:  # pd.Interval
    #         mask = (s.index >= irng.left) & (s.index <= irng.right)
    #         s[mask] = np.nan
    #     # Lower and Upper replacement intervals (see HarvestIT #177)
    #     s = self._replace_lower(s, sensor)
    #     s = self._replace_upper(s, sensor)
    #
    #     return s


    def _process_data__native(self, sensor, s_raw):
        """This is the main data processing method, it implements e.g. min max filtering, plant.ignored_ranges etc.
        This method is intended for sensor data which is given as numeric pd.Series, not dtype pint, to accelerate
        runtime.

        Parameters
        ----------
        sensor : Sensor
        s_raw : pd.Series
            Unprocessed data for sensor, with float (or equiv.) dtype, typically obtained from self.get_sensor_data()

        Returns
        -------
        s : pd.Series
            Processed data for sensor, with numeric dtype.
        """
        s = s_raw
        # Set values in ignored ranges to NaN
        for irng in self.plant.ignored_ranges:  # pd.Interval
            mask = (s.index >= irng.left) & (s.index <= irng.right)
            s[mask] = np.nan
        # Lower and Upper replacement intervals (see HarvestIT #177)
        s = self._replace_lower__native(s, sensor)
        s = self._replace_upper__native(s, sensor)

        return s

    def _assert_datasource_df_db(self):
        if self.datasource is None:
            raise ConfigurationError('Context datasource is None.')
        if self.datasource not in ['df', 'db']:
            raise ConfigurationError(f'Unexpected Context datasource {self.datasource}.')

    def verify_time_index(self):
        """Make sure context has a valid time index."""
        self.time_index
        return

    @staticmethod
    def _replace_lower__native(data, sensor):
        """Implement lower replacement interval, see #177.

        Parameters
        ----------
        data : pd.Series with unprocessed data
        sensor : Sensor

        Returns
        -------
        s : pd.Series with replaced values.
        """
        left, right, replace = sensor.value_replacements__native['lower']
        if (left is None) and (right is None) and (replace is None):
            # all None: nothing to do
            return data

        if right is None and replace is None:
            # no replacement value given, only left is not None
            data[data < left] = np.nan
            return data

        if left is None and replace is None:
            # no replacement value given, only right is not None
            data[data < right] = np.nan
            return data

        if left is None:
            data[data < right] = replace
            return data

        # all are not-NaN
        data[data < left] = np.nan
        data[(data >= left) & (data < right)] = replace
        # Does not work, package incompatibility... s[(s >= left) & (s < right)] = replace
        return data

    @staticmethod
    def _replace_upper__native(data, sensor):
        """Implement upper replacement interval, see #177.

        Parameters
        ----------
        data : pd.Series with unprocessed data
        sensor : Sensor

        Returns
        -------
        s : pd.Series with replaced values.
        """
        left, right, replace = sensor.value_replacements__native['upper']
        if (left is None) and (right is None) and (replace is None):
            # all None: nothing to do
            return data

        if left is None and replace is None:
            # no replacement value given, only right is not None
            data[data > right] = np.nan
            return data

        if right is None and replace is None:
            # no replacement value given, only left is not None
            data[data > left] = np.nan
            return data

        if right is None:
            data[data > left] = replace
            return data

        # all are not-NaN
        data[data > right] = np.nan
        data[(data > left) & (data <= right)] = replace
        return data

    # @staticmethod
    # def _replace_lower(data, sensor):
    #     """Implement lower replacement interval, see #177.
    #
    #     Parameters
    #     ----------
    #     data : pd.Series with unprocessed data
    #     sensor : Sensor
    #
    #     Returns
    #     -------
    #     s : pd.Series with replaced values.
    #     """
    #     left, right, replace = sensor.value_replacements['lower']
    #     if (left is None) and (right is None) and (replace is None):
    #         # all None: nothing to do
    #         return data
    #
    #     if right is None and replace is None:
    #         # no replacement value given, only left is not None
    #         data[data < left] = np.nan
    #         return data
    #
    #     if left is None and replace is None:
    #         # no replacement value given, only right is not None
    #         data[data < right] = np.nan
    #         return data
    #
    #     if left is None:
    #         data[data < right] = replace.to(sensor.native_unit).magnitude
    #         return data
    #
    #     # all are not-NaN
    #     data[data < left] = np.nan
    #     data[(data >= left) & (data < right)] = replace.to(sensor.native_unit).magnitude
    #     # Does not work, package incompatibility... s[(s >= left) & (s < right)] = replace
    #     return data
    #
    # @staticmethod
    # def _replace_upper(data, sensor):
    #     """Implement upper replacement interval, see #177.
    #
    #     Parameters
    #     ----------
    #     data : pd.Series with unprocessed data
    #     sensor : Sensor
    #
    #     Returns
    #     -------
    #     s : pd.Series with replaced values.
    #     """
    #     left, right, replace = sensor.value_replacements['upper']
    #     if (left is None) and (right is None) and (replace is None):
    #         # all None: nothing to do
    #         return data
    #
    #     if left is None and replace is None:
    #         # no replacement value given, only right is not None
    #         data[data > right] = np.nan
    #         return data
    #
    #     if right is None and replace is None:
    #         # no replacement value given, only left is not None
    #         data[data > left] = np.nan
    #         return data
    #
    #     if right is None:
    #         data[data > left] = replace.to(sensor.native_unit).magnitude
    #         return data
    #
    #     # all are not-NaN
    #     data[data > right] = np.nan
    #     data[(data > left) & (data <= right)] = replace.to(sensor.native_unit).magnitude
    #     return data

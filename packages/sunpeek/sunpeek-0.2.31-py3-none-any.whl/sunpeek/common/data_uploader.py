"""
Implements the data ingestion process as roughly described in HarvestIT #187.
Data source backend can either be DataFrame or database (as implemented in Context class).
This module implements the same data ingestion process for both data sources.

Instantiate with DataUploader_df or DataUploader_db,
then do_upload() to trigger the upload.

Data ingestion is implemented in this module. Data stored (in database or dataframe) have gone through some
sanity checking. As a result, we can rely on having a timezone-aware, sorted datetime index with no duplicates,
data is either numeric or NaN, all component slots are populated with data.
The same import & sanity procedures are used for both database and dataframe backend.
Any further, dynamic data processing steps are done on-the-fly (see `Context` class), things like ignored intervals and
min-max replacement intervals.
In this way, for instance, an ignored range can be added or deleted in a plant, and sensor data will behave
accordingly. This is implemented in common.context.

Data ingestion triggers virtual sensor calculation.
do_upload() returns data quality check ("sensor validation"), available as per-day and per-sensor information.

Notes
-----
Main method is do_upload() which returns the upload response in a dict. What it does:
- checks timezone info in csv files
- handles strings in data
- sorts timestamps and drops duplicates
- calculates virtual sensors
- calls sensor validation and kernel method validation
- uploads data to store in raw_data table in db#
"""

import os
import warnings
import pathlib

import numpy as np
from typing import List, Union
import time
import pandas as pd
import pytz
from io import BytesIO
from typing import Dict
from pydantic import validator
import enum

import sunpeek.common.time_zone
from sunpeek.common.utils import sp_logger
from sunpeek.common.context import Context, import_db_ops
import datetime

from sunpeek.base_model import BaseModel
from sunpeek.common.context import sanitize_dataframe
from sunpeek.common.errors import DataProcessingError, TimeZoneError
from sunpeek.db_utils import DATETIME_COL_NAME


class DataUploadResponseFile(BaseModel):
    name: Union[str, None]
    exists: Union[bool, None]
    size_bytes: Union[int, None]
    missing_columns: Union[List[str], None]
    error_cause: Union[str, None]


class DataUploadResponse(BaseModel):
    n_uploaded_data_rows: Union[int, None]
    n_duplicates_index: Union[int, None]
    response_per_file: Union[List[DataUploadResponseFile], None]
    sensor_validation: Union[Dict[str, str], None]
    db_response: Union[dict, None]

    @validator('sensor_validation', pre=True)
    def df_to_val(cls, dct):
        if dct is not None:
            return {k: v.to_json(date_format='iso') for k, v in dct.items() if not isinstance(v, str)}


class DataColumnsResponse(BaseModel):
    sensors: Union[List[str], None]
    index: Union[str, None]


class DatetimeTemplates(enum.Enum):
    year_month_day = "year_month_day"
    day_month_year = "day_month_year"
    month_day_year = "month_day_year"


class DataUploader_df:
    """
    Data uploads of csv files to a plant using Context backend with datasource 'dataframe'.

    Parameters
    ----------
    files : list
        List of csv files to import.
    plant : Plant
        A configured plant.
    timezone : str
        Optional. Time zone information, if not given in the csv data.

    Notes
    -----
    - This class does not need and not use the database. Use DataUploader_db for database backend.
    - The csv files need not be in chronological order.
    - Number of columns needs not be the same across files.
    - Time zone information must either be given in csv timestamps or as timezone.
    """

    def __init__(self,
                 plant,
                 datetime_template: DatetimeTemplates = None,
                 datetime_format: str = None,
                 timezone: Union[str, pytz.timezone] = None,
                 csv_separator: str = ';',
                 csv_decimal: str = '.',
                 csv_encoding: str = 'utf-8',
                 index_col: int = 0,
                 eval_start: datetime.date = None,
                 eval_end: datetime.date = None,
                 on_file_error: str = 'report',
                 ):
        """
        Parameters
        ----------
        plant : Plant
        files : UploadFile, str, os.PathLike
            Files to upload.
        timezone : str or pytz.timezone.
            Optional. To be provided if timestamps in the data have no time zone information.
        csv_separator : str
            Used in pd.read_csv as 'sep' kwarg
        csv_decimal : str
            Used in pd.read_csv as 'decimal' kwarg
        csv_encoding : str
            Used in pd.read_csv as 'encoding' kwarg
        datetime_format : str
            Used to parse datetimes from csv file. Leave to None infers the format.
        index_col : int
            DataUploader will try to parse timestamps from this column.
        eval_start : datetime
            Limit the data that is read and imported
        eval_end : datetime
            Limit the data that is read and imported
        on_file_error : str
            Behaviour if an error is encountered reading a file, either `report` to store details in the file response
            and continue, or `raise`, to raise the error and stop.
        """
        self.plant = plant
        self.eval_start = eval_start
        self.eval_end = eval_end
        self.output = DataUploadResponse()

        if (datetime_template is None) and (datetime_format is None):
            raise DataProcessingError('Either "datetime_template" or "datetime_format" needs to be specified.')

        if isinstance(datetime_template, str):
            self.datetime_template = DatetimeTemplates[datetime_template]
        else:
            self.datetime_template = datetime_template

        self.datetime_format = datetime_format

        self.timezone = timezone
        self.csv_decimal = csv_decimal
        self.index_col = index_col
        self.on_file_error = on_file_error

        self.read_csv = \
            lambda x, **kwargs: pd.read_csv(x,
                                            encoding=csv_encoding,
                                            sep=csv_separator,
                                            on_bad_lines='skip',
                                            parse_dates=False,
                                            dtype='str',
                                            **kwargs)

    def __validate_files(self, files):
        if files is None:
            raise DataProcessingError('No files to upload supplied.')
        if not isinstance(files, list):
            files = [files]
        if not (len(files) > 0):
            raise DataProcessingError('No files to upload supplied.')
        return files

    def do_upload(self, files, calculate_virtuals: bool = True):
        """Full measurement data ingestion process, also triggers virtual sensor calculation and sensor validation.

        Parameters
        ----------
        calculate_virtuals : bool
            Whether to trigger virtual sensor calculation.

        Raises
        ------
        FileNotFoundError
        ConnectionError

        Returns
        -------
        dict : Response from the data upload, various info fields including sensor validation etc.
        """
        self.files = self.__validate_files(files)

        start_time = time.time()
        self._pre_upload()

        # Full data ingestion process, common for all context datasources (database, dataframe).
        self._csv_to_plant(calculate_virtuals)

        self._post_upload()
        sp_logger.debug(f"[data_uploader] --- Finished after {(time.time() - start_time):.1f} seconds ---")

        return self.output

    def _csv_to_plant(self, calculate_virtuals: bool):
        """Full data ingestion process, from csv to plant with dataframe context.
        Reads csv files to DataFrame, sets plant context datasource, does sensor validation.

        Returns
        -------
        sensor_validation : dict
        """
        df = self._all_csv_to_single_df()

        sensor_validation = self.plant.use_dataframe(df, calculate_virtuals=calculate_virtuals)
        self.output.sensor_validation = sensor_validation

        return sensor_validation

    def _all_csv_to_single_df(self):
        """Concatenates the uploaded csv files into a single df.

        Returns
        -------
        df_all_files : pd.DataFrame

        Raises
        ------
        AssertionError

        Notes
        -----
        - Columns which do not match with any of the plant's sensor raw_names are dropped.
        - Works for fastAPI's UploadFile as well as for normal csv files.
        """
        sp_logger.debug(f"[data_uploader] Reading csv files to DataFrame.")
        sp_logger.debug(f"[data_uploader] Concatenating {len(self.files)} files.")
        start_time = time.time()

        # Iterate trough files and gather DataFrames
        df_all_files = None
        self.output.response_per_file = []
        for file in self.files:
            file_response = DataUploadResponseFile()
            try:
                # is either a FlaskApi File or file-path, or a BytesIO object
                if hasattr(file, 'filename'):
                    file_response.name = file.filename
                    file_response.exists = True
                elif isinstance(file, str) or isinstance(file, pathlib.Path):
                    file_response.name = os.path.basename(file)
                    file_response.exists = os.path.exists(file)
                elif isinstance(file, BytesIO):
                    file_response.name = None
                    file_response.exists = True
                else:
                    raise FileNotFoundError(f'Cannot interpret input for file: "{file}".')

                if not file_response.exists:
                    raise FileNotFoundError(f'Cannot find file: "{file_response.name}".')

                # Create BytesIO object
                bio = self._to_BytesIO(file)

                # get size
                bio.seek(0, os.SEEK_END)
                file_response.size_bytes = bio.tell()
                bio.seek(0)

                try:
                    df_file, missing_columns = self._one_csv_to_df(bio)
                except (ValueError, TimeZoneError) as ex:
                    sp_logger.exception(ex)
                    if self.on_file_error == 'raise':
                        raise
                    file_response.error_cause = f'Error: {ex}'
                    continue
                file_response.missing_columns = missing_columns

                # Concatenate the dataframes
                if len(df_file) > 0:
                    df_all_files = pd.concat([df_all_files, df_file], ignore_index=False)
                    if not isinstance(df_all_files.index, pd.DatetimeIndex):
                        raise DataProcessingError('Cannot concatenate DataFrames with mixed timezones since this '
                                                  'results in the DataFrame index not being a DatetimeIndex anymore.')

            finally:
                self.output.response_per_file.append(file_response)

        # Check for duplicates etc.
        df_all_files, n_duplicates_index = sanitize_dataframe(df_all_files)
        self.output.n_duplicates_index = n_duplicates_index
        if self.output.n_duplicates_index:
            duplicate_warning = f"Found {self.output.n_duplicates_index} duplicate index entries in data. " \
                                f"All rows with duplicate index will be removed."
            sp_logger.warning(duplicate_warning)
            warnings.warn(duplicate_warning)

        if (df_all_files is None) or len(df_all_files) < 2:
            df_all_files = None
            self.output.n_uploaded_data_rows = 0
            df_none_warning = 'Reading csv files resulted in a DataFrame with less than 2 rows.'
            sp_logger.warning(df_none_warning)
            warnings.warn(df_none_warning)
            # raise DataProcessingError('Reading csv files resulted in a DataFrame with less than 2 rows.')
        else:
            self.output.n_uploaded_data_rows = len(df_all_files)

        sp_logger.debug(
            f"[data_uploader] --- Done parsing {len(self.files)} files in {(time.time() - start_time):.1f} seconds.")

        return df_all_files

    @staticmethod
    def _to_BytesIO(bio_or_file):  # noqa
        if hasattr(bio_or_file, 'filename'):
            bio = bio_or_file.file
        elif isinstance(bio_or_file, BytesIO):
            bio = bio_or_file
        else:
            with open(bio_or_file, 'rb') as f:
                bio = BytesIO(f.read())
        return bio

    def _one_csv_to_df(self, bio):
        """Read a BytesIO object to DataFrame.

        Parameters
        ----------
        bio : BytesIO object
            From an UploadFile or from a normal csv file.

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with tz-aware DatetimeIndex
        missing_columns : List[str]
            Columns not found in the file

        Raises
        ------
        AssertionError

        Notes
        -----
        - Returns a DataFrame with DatetimeIndex taken from the first column, index is named according to
         sunpeek.db_utils.DATETIME_COL_NAME.
        - Missing columns are added as all-NaN columns.
        """
        # Parse timestamps from first column
        ds_cache = self._parse_timestamps(bio)
        try:
            skiprows = ds_cache.isna()
            # Limit the rows to read in the file, if bounds were provided
            if self.eval_start is not None:
                skiprows = skiprows | (ds_cache < self.eval_start)
            if self.eval_end is not None:
                skiprows = skiprows | (ds_cache > self.eval_end)
            ds_cache = ds_cache[~skiprows]
            # convert to numbers, for pd.read_csv()
            skiprows = [i for i, x in enumerate(np.insert(skiprows, 0, False)) if x]

            # Main read_csv call
            bio.seek(0)
            df = self.read_csv(bio,
                               usecols=lambda x: x in self.plant.get_raw_names(include_virtuals=False),
                               skiprows=skiprows)
            # read_csv with decimal kwarg fails when reading string, hence the two calls to apply()
            if self.csv_decimal is not None:
                df = df.apply(lambda x: x.str.replace(self.csv_decimal, '.'))
            df = df.apply(pd.to_numeric, errors='coerce')
            df = pd.DataFrame(index=ds_cache) if df.empty else df.set_index(ds_cache)
            df = df.rename_axis(DATETIME_COL_NAME)

            # Add missing real sensor column names as NaN columns
            missing_columns = set(self.plant.get_raw_names(include_virtuals=False)) - set(df.columns)
            df[list(missing_columns)] = np.nan

            return df, list(missing_columns)

        except Exception as ex:
            sp_logger.exception(ex)
            warnings.warn(f'Failed to read csv file using pandas read_csv. {ex}')
            raise ValueError(f'Failed to read csv file using pandas read_csv. {ex}') from ex

    def get_sensor_names(self, files):
        """returns names of the sensors based on an example file (or BytesIO)"""
        files = self.__validate_files(files)
        bio = self._to_BytesIO(files[0])
        bio.seek(0)
        df = self.read_csv(bio, nrows=1, index_col=self.index_col)
        return df.columns

    def get_index_name(self, files):
        """returns name of the index column based on an example file (or BytesIO)"""
        files = self.__validate_files(files)
        bio = self._to_BytesIO(files[0])
        bio.seek(0)
        df = self.read_csv(bio, nrows=1, index_col=self.index_col, usecols=[])
        return df.index.name

    def _parse_timestamps(self, bio):
        """Parse timestamps from first column in bio, validate timezone, return tz-aware DatetimeIndex
        """
        bio.seek(0)
        ds = self.read_csv(bio, usecols=[self.index_col]).iloc[:, 0]
        # In parsing timestamps, priority is given to the more explicit self.datetime_format:
        if self.datetime_format is not None:
            ds = pd.to_datetime(ds, errors='coerce', format=self.datetime_format)
        else:
            dayfirst = True if (self.datetime_template == DatetimeTemplates.day_month_year) else False
            yearfirst = True if (self.datetime_template == DatetimeTemplates.year_month_day) else False
            try:
                ds = pd.to_datetime(ds, errors='coerce', dayfirst=dayfirst, yearfirst=yearfirst)
            except (pd.errors.ParserError, ValueError) as e:
                raise DataProcessingError(
                    f"Pandas to_datetime was unable to parse timestamps from the file, given datetime_template="
                    f"{self.datetime_template}. Try to set an explicit 'datetime_format' instead.")
        # Does not parse timezone-aware datetimes correctly, e.g. '2017-04-30 00:00:00+00:00' is parsed as NaT:
        # ds = pd.to_datetime(ds, errors='coerce', infer_datetime_format=True)

        try:
            ds = pd.DatetimeIndex(ds)
        except:
            # Mixed timezone timestamp columns lead to Index class df.index with dtype 'object'
            # see https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
            raise TimeZoneError(
                '[data_uploader] Could not convert timestamps of the csv file to a DatetimeIndex. '
                'One cause why this happens are mixed-timezone timestamps or only some rows having timezones.')

        ds = sunpeek.common.time_zone.validate_timezone(ds, self.timezone)

        return ds

    def _pre_upload(self):
        pass

    def _post_upload(self):
        pass


class DataUploader_db(DataUploader_df):
    """Data upload from csv files to database.
    """

    def __init__(self, session, **kwargs):
        super().__init__(**kwargs)
        self._sensor_raw_names = None
        self.output.db_response = {}
        # Try to establish database connection, raises ConnectionError
        self.db_connection = import_db_ops().get_db_connection()
        self.session = session

    @property
    def table_name(self):
        return self.plant.raw_table_name

    def _get_types_dict(self):
        types_dict = {DATETIME_COL_NAME: datetime.datetime}
        for sensor in self.plant.raw_sensors:
            if getattr(sensor.sensor_type, 'name', '') == 'bool':
                types_dict[sensor.raw_name] = bool
            elif getattr(sensor.sensor_type, 'compatible_unit_str', '') == 'str':
                types_dict[sensor.raw_name] = str
            else:
                types_dict[sensor.raw_name] = float

        return types_dict

    def _create_raw_data_table(self):
        """Creates raw data table if it does not exists in the database.
        """
        # Create database inferring runtime types
        try:
            types_dict = self._get_types_dict()
            import_db_ops().create_table_dynamic(self.session.get_bind(), self.table_name, types_dict)
            self.output.db_response['new_table_created'] = True
            self.output.db_response['new_table_name'] = self.table_name

        except Exception as ex:
            sp_logger.exception(ex)
            raise

    def _update_table(self):
        types_dict = self._get_types_dict()
        import_db_ops().create_new_data_cols(self.session.get_bind(), self.table_name, types_dict)

    def _pre_upload(self):
        table_exists = import_db_ops().db_table_exists(self.session.get_bind(), self.table_name)
        if table_exists:
            sp_logger.debug(f"[data_uploader] Table {self.table_name} exists in database. Adding columns for any "
                            f"new sensors for plant {self.plant.name}.")
            self._update_table()
        else:
            sp_logger.debug(f"[data_uploader] Creating table {self.table_name} in database.")
            self._create_raw_data_table()

    def _post_upload(self):
        """Save dataframe to database
        """
        df = self.plant.context.df
        if df is not None:
            # Before writing to database, any overlapping (not only duplicate) data in db is deleted.
            sp_logger.debug(f"[data_uploader] Deleting overlapping data from table {self.table_name}.")
            self.output.db_response['overlap_response'] = \
                import_db_ops().delete_overlapping_data(self.db_connection, self.table_name,
                                                        overlapping_boundaries=(df.index[0], df.index[-1]))

            for name in [s.raw_name for s in self.plant.raw_sensors if getattr(s.sensor_type, 'name', '') == 'bool']:
                df[name] = df[name].astype(bool)

            # Write new data (including virtual sensors) to db.
            sp_logger.debug(f"[data_uploader] Writing dataframe to table {self.table_name}...")
            self.output.db_response['measure_data_saved_db_ok'] = import_db_ops().df_to_db(self.db_connection, df,
                                                                                           self.table_name)
            if self.output.db_response['measure_data_saved_db_ok']:
                self.db_connection.commit()
                sp_logger.debug(f"[data_uploader] Data succesfully saved in db table {self.table_name}.")
                import_db_ops().disconnect_db(self.db_connection)
            else:
                sp_logger.debug(f"[data_uploader] Error writing data to db table {self.table_name}.")
                self.db_connection.rollback()
                import_db_ops().disconnect_db(self.db_connection)
                raise ConnectionError('Failed to store data in database table.')

        # From now on, data is accessed by 'db' and uses the full datetime range available in the db
        self.plant.context = Context(plant=self.plant, datasource='db',
                                     eval_start=self.eval_start, eval_end=self.eval_end)

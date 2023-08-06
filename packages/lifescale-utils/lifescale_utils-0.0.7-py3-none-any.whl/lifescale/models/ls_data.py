"""Modelling the data output of a LifeScale run.

Copyright (C) 2023  Andreas Hellerschmied <heller182@gmx.at>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import datetime as dt
import numpy as np
import os
import pandas as pd


class LSData:
    """Modelling the data output of a LifeScale run.

    Attributes
    ----------
    run_name : str
        Name of the LifeScale run.
    input_xlsm_filename : str
        Filename and path of the xlsm file written by LifeScale.
    output_dir_path : str
        Output directory filepath.
    start_time_dt : datetime object
        Start time of run.
    end_time_dt : datetime object
        End time of the run.
    settings_dict : dict
        Contains all settings from the Settings sheet of the input xlsm file. If more than one attributes are provides
        for a parameter (dictionary key), the dictionary item is a list. If no attribute is provided, the item is `None`
    df_panel_data : pandas dataframe
        Pandas dataframe that holds the data of the PanelData sheet of the input xlsm file.
    df_interval_analysis : pandas dataframe
        Pandas dataframe that holds the data of the IntervalAnalysis sheet plus additional data of the input xlsm file.
    df_masses : pandas dataframe
        Pandas dataframe that holds the data derived from the AcquisitionIntervals sheet of the input xlsm file.
    """

    def __init__(self,
                 run_name='',
                 guid='',
                 input_xlsm_filename='',
                 output_dir_path='',
                 start_time_dt=None,
                 end_time_dt=None,
                 settings_dict=None,
                 df_panel_data=None,
                 df_interval_analysis=None,
                 df_masses=None,
                 ):
        """Default constructor of class LSData."""

        # Check input arguments:

        # run_name and accession number:
        if isinstance(run_name, str):
            self.run_name = run_name
        else:
            raise TypeError('"run_name" needs to be a string')
        if isinstance(guid, str):
            self.guid = guid
        else:
            raise TypeError('"guid" needs to be a string')

        # output_dir_path:
        if isinstance(output_dir_path, str):
            self.output_dir_path = output_dir_path
        else:
            raise TypeError('"data_dir_path" needs to be a string')

        # xlsm_filename:
        if isinstance(input_xlsm_filename, str):
            self.input_xlsm_filename = input_xlsm_filename
        else:
            raise TypeError('"xlsm_filename" needs to be a string')

        # Start and end time of the run:
        if isinstance(start_time_dt, dt.datetime):
            self.start_time_dt = start_time_dt
        else:
            raise TypeError('"start_time_dt" needs to be a datetime object')
        if isinstance(end_time_dt, dt.datetime):
            self.end_time_dt = end_time_dt
        else:
            raise TypeError('"end_time_dt" needs to be a datetime object')
        if isinstance(end_time_dt, dt.datetime):
            self.end_time_dt = end_time_dt
        else:
            raise TypeError('"end_time_dt" needs to be a datetime object')

        # Settings dict:
        if isinstance(settings_dict, dict):
            self.settings_dict = settings_dict
        else:
            raise TypeError('"settings_dict" needs to be a dict.')

        # Dataframes:
        if isinstance(df_panel_data, pd.DataFrame):
            self.df_panel_data = df_panel_data
        else:
            raise TypeError('"df_panel_data" needs to be a pandas dataframe.')
        if isinstance(df_interval_analysis, pd.DataFrame):
            self.df_interval_analysis = df_interval_analysis
        else:
            raise TypeError('"df_interval_analysis" needs to be a pandas dataframe.')
        if isinstance(df_masses, pd.DataFrame):
            self.df_masses = df_masses
        else:
            raise TypeError('"df_masses" needs to be a pandas dataframe.')

        # Initialize additional attributes:
        pass

    @classmethod
    def from_xlsm_file(cls, input_xlsm_filename, verbose=True):
        """Constructor that generates and populates the LSData object from an xlsm LS output file.

        Parameters
        ----------
        input_xlsm_filename : str
            Filename and path of the xlsm file written by LifeScale.
        verbose : bool, optional (default = `True`)
            If `True`, status messages are written to the command line.

        Returns
        -------
        :py:obj:`.LSData`
            Contains all LS output data loaded from the given xlsm file.
        """

        REQUIRED_XLSM_SHEET_NAMES = [  # Raise an exception if they are not present in the input xlsm file.
            'AcquisitionIntervals',
            'IntervalAnalysis',
            'PanelData',
            'Settings',
        ]

        # Check input data:
        # input_xlsm_filename:
        if not input_xlsm_filename:
            raise AssertionError(f'The parameter "input_xlsm_filename" must not be empty!')
        if not isinstance(input_xlsm_filename, str):
            raise TypeError('"input_xlsm_filename" needs to be a string')
        if not os.path.isfile(input_xlsm_filename):
            raise AssertionError(f'XLSM file {input_xlsm_filename} does not exist!')

        # Load all needed sheets of the xlsm file to pandas dataframes:
        if verbose:
            print(f'Load data from xlsm file: {input_xlsm_filename}')

        # Get sheet names:
        xl_file = pd.ExcelFile(input_xlsm_filename)
        sheet_names = xl_file.sheet_names

        # Check, if all required sheets are available:
        if set(REQUIRED_XLSM_SHEET_NAMES) - set(sheet_names):
            missing_sheets = list(set(REQUIRED_XLSM_SHEET_NAMES) - set(sheet_names))
            raise AssertionError(f'The following sheets are missing the file {input_xlsm_filename}: {missing_sheets}')

        # PanelData:
        if verbose:
            print(f' - Parse PanelData')
        df_panel_data = xl_file.parse('PanelData')
        df_panel_data = remove_space_from_column_names(df_panel_data)
        df_panel_data['NumberOfIntervals'] = None
        if not (df_panel_data[['Id']].value_counts().count() == len(df_panel_data)):
            raise AssertionError(
                f'The values in the column "Id" in PanelData is not unique!')

        # IntervalAnalysis:
        if verbose:
            print(f' - Parse IntervalAnalysis')
        df_interval_analysis = xl_file.parse('IntervalAnalysis')
        df_interval_analysis = remove_space_from_column_names(df_interval_analysis)
        df_interval_analysis['Status'] = None  # From AcquisitionIntervals
        df_interval_analysis['DetectedParticles'] = None  # From AcquisitionIntervals
        df_interval_analysis['MeasuredVolume'] = None  # From AcquisitionIntervals
        df_interval_analysis['ResonantFrequency'] = None  # From AcquisitionIntervals
        if not (df_interval_analysis[['Id', 'IntervalNumber']].value_counts().count() == len(df_interval_analysis)):
            raise AssertionError(
                f'The combination if the values in the columns "Id" and "IntervalNumber" in IntervalAnalysis is not '
                f'unique!')
        df_interval_analysis['SampleID'] = df_interval_analysis['Well'] + '-' + df_interval_analysis[
            'IntervalNumber'].astype(str)
        df_interval_analysis['keep_min_mass'] = None  # Masses threshold
        df_interval_analysis['keep_max_mass'] = None  # Masses threshold

        # Settings:
        if verbose:
            print(f' - Parse Settings')
        settings_dict = {}
        df_tmp = xl_file.parse('Settings', header=None)
        for idx, row in df_tmp.iterrows():
            short_row = row[1:]
            item_not_nan_max_idx = short_row.loc[~short_row.isna()].index.max()
            if item_not_nan_max_idx is np.nan:  # No items that are not NaN!
                settings_dict[row[0]] = None
            else:
                tmp_list = short_row.loc[:item_not_nan_max_idx].to_list()
                num_items = len(tmp_list)
                if num_items == 1:
                    settings_dict[row[0]] = tmp_list[0]
                else:
                    settings_dict[row[0]] = tmp_list
        run_name = settings_dict['Name']
        if settings_dict['Guid'] is None:
            guid = ''
        else:
            guid = str(settings_dict['Guid'])
        start_time_dt = settings_dict['StartTime']
        end_time_dt = start_time_dt + dt.timedelta(settings_dict['ElapsedTime'] / (24 * 60))

        # # Settings (dataframe):
        # df_settings = xl_file.parse('Settings', header=None).transpose()
        # df_settings.columns = df_settings.iloc[0]
        # df_settings = df_settings[1:]
        # df_settings.reset_index(drop=True, inplace=True)

        # Masses (from sheet AcquisitionIntervals):
        if verbose:
            print(f' - Parse Masses')
        id_list = []
        well_list = []
        interval_num_list = []
        time_list = []
        masses_list = []
        volume_list = []
        total_num_particles_list = []
        transit_time_list = []
        pressure_drop_list = []
        time_list_length_old = 0
        # masses_list_length_old = 0
        # volume_list_length_old = 0
        # total_num_particles_list_length_old = 0
        # transit_time_list_length_old = 0
        # pressure_drop_list_length_old = 0

        current_id = None
        current_well = None
        current_interval_num = None
        current_detected_particles = None

        df_tmp = xl_file.parse('AcquisitionIntervals', header=None)
        for ids, row in df_tmp.iterrows():
            if row[0] == 'Id':
                current_id = row[1]
                if ~(df_interval_analysis['Id'] == current_id).any():
                    raise AssertionError(f'"ID="{current_id} is not available in IntervalAnalysis!')
                if ~(df_panel_data['Id'] == current_id).any():
                    raise AssertionError(f'"ID="{current_id} is not available in PanelData!')
                continue
            if row[0] == 'Well':
                current_well = row[1]
                if ~(df_interval_analysis['Well'] == current_well).any():
                    raise AssertionError(f'"Well="{current_well} is not available in IntervalAnalysis!')
                if ~(df_panel_data['Well'] == current_well).any():
                    raise AssertionError(f'"Well="{current_well} is not available in PanelData!')
                continue
            if row[0] == 'Antibiotic':
                continue
            if row[0] == 'AntibioticConcentration':
                continue
            if row[0] == 'NumberOfIntervals':
                df_panel_data.loc[df_panel_data['Id'] == current_id, 'NumberOfIntervals'] = row[1]
                continue
            if row[0] == 'IntervalNumber':
                current_interval_num = row[1]
                if ~(df_interval_analysis['IntervalNumber'] == current_interval_num).any():
                    raise AssertionError(
                        f'"IntervalNumber="{current_interval_num} is not available in IntervalAnalysis!')
                continue
            if row[0] == 'StartTime':
                continue
            if row[0] == 'EndTime':
                continue
            if row[0] == 'DilutionFactor':
                continue
            if row[0] == 'Status':
                tmp_filter = (df_interval_analysis['Id'] == current_id) & (
                        df_interval_analysis['IntervalNumber'] == current_interval_num)
                if len(tmp_filter[tmp_filter]) != 1:
                    raise AssertionError(
                        f'Invalid number of matches of "Id={current_id}" and "IntervalNumber={current_interval_num}" '
                        f'in IntervalAnalysis: {len(tmp_filter[tmp_filter])}')
                df_interval_analysis.loc[tmp_filter, 'Status'] = row[1]
                continue
            if row[0] == 'DetectedParticles':
                tmp_filter = (df_interval_analysis['Id'] == current_id) & (
                        df_interval_analysis['IntervalNumber'] == current_interval_num)
                if len(tmp_filter[tmp_filter]) != 1:
                    raise AssertionError(
                        f'Invalid number of matches of "Id={current_id}" and "IntervalNumber={current_interval_num}" '
                        f'in IntervalAnalysis: {len(tmp_filter[tmp_filter])}')
                df_interval_analysis.loc[tmp_filter, 'DetectedParticles'] = row[1]
                current_detected_particles = row[1]  # For cross-checks
                continue
            if row[0] == 'MeasuredVolume':
                tmp_filter = (df_interval_analysis['Id'] == current_id) & (
                        df_interval_analysis['IntervalNumber'] == current_interval_num)
                if len(tmp_filter[tmp_filter]) != 1:
                    raise AssertionError(
                        f'Invalid number of matches of "Id={current_id}" and "IntervalNumber={current_interval_num}" '
                        f'in IntervalAnalysis: {len(tmp_filter[tmp_filter])}')
                df_interval_analysis.loc[tmp_filter, 'MeasuredVolume'] = row[1]
                continue
            if row[0] == 'ResonantFrequency':
                tmp_filter = (df_interval_analysis['Id'] == current_id) & (
                        df_interval_analysis['IntervalNumber'] == current_interval_num)
                if len(tmp_filter[tmp_filter]) != 1:
                    raise AssertionError(
                        f'Invalid number of matches of "Id={current_id}" and "IntervalNumber={current_interval_num}" '
                        f'in IntervalAnalysis: {len(tmp_filter[tmp_filter])}')
                df_interval_analysis.loc[tmp_filter, 'ResonantFrequency'] = row[1]
                continue
            if row[0] == 'Time':
                tmp_list = row_to_list(row[1:])
                if (len(tmp_list) == 0) and (current_detected_particles != 0):
                    raise AssertionError(
                        f'Number of "DetectedParticles={current_detected_particles}" does not match length of "Time" '
                        f'series (= {len(tmp_list)}) ')
                time_list += tmp_list
                continue
            if row[0] == 'Mass':
                tmp_list = row_to_list(row[1:])
                masses_list += tmp_list
                continue
            if row[0] == 'Volume':
                tmp_list = row_to_list(row[1:])
                volume_list += tmp_list
                continue
            if row[0] == 'TotalNumberOfParticlesThroughSensor':
                tmp_list = row_to_list(row[1:])
                total_num_particles_list += tmp_list
                continue
            if row[0] == 'TransitTime':
                tmp_list = row_to_list(row[1:])
                transit_time_list += tmp_list
                continue
            if row[0] == 'PressureDrop':
                tmp_list = row_to_list(row[1:])
                pressure_drop_list += tmp_list

                # Finish data collection for the current Interval (sample):
                # Check if the length of all data series of the current interval number match:
                if not (len(time_list) == len(masses_list) == len(volume_list) == len(total_num_particles_list) == len(
                        transit_time_list) == len(pressure_drop_list)):
                    raise AssertionError(
                        f'The lengths of the data series in AcquisitionIntervals of "Well={current_well}" and '
                        f'"IntervalNumber={current_interval_num}" do not match!')
                # Set up lists for well, id and interval number:
                num_additional_items_in_data_series = len(time_list) - time_list_length_old
                tmp_list = [current_id] * num_additional_items_in_data_series
                id_list += tmp_list
                tmp_list = [current_well] * num_additional_items_in_data_series
                well_list += tmp_list
                tmp_list = [current_interval_num] * num_additional_items_in_data_series
                interval_num_list += tmp_list
                # Reset counters:
                time_list_length_old = len(time_list)
                # masses_list_length_old = len(masses_list)
                # volume_list_length_old = len(volume_list)
                # total_num_particles_list_length_old = len(total_num_particles_list)
                # transit_time_list_length_old = len(transit_time_list)
                # pressure_drop_list_length_old = len(pressure_drop_list)
                continue

        # Check if the length of all data series lists match:
        if not (len(time_list) == len(masses_list) == len(volume_list) == len(total_num_particles_list) == len(
                transit_time_list) == len(pressure_drop_list) == len(id_list) == len(well_list) == len(
                interval_num_list)):
            raise AssertionError(
                f'The lengths of the data series in AcquisitionIntervals do not match!')

        # Create dataframe:
        df_masses_columns = ['Id', 'Well', 'IntervalNumber', 'Time', 'Mass', 'Volume',
                             'TotalNumberOfParticlesThroughSensor', 'TransitTime', 'PressureDrop']
        df_masses = pd.DataFrame(list(
            zip(id_list, well_list, interval_num_list, time_list, masses_list, volume_list, total_num_particles_list,
                transit_time_list, pressure_drop_list)),
            columns=df_masses_columns)
        df_masses['Id'] = df_masses['Id'].astype(int)
        df_masses['IntervalNumber'] = df_masses['IntervalNumber'].astype(int)
        df_masses['SampleID'] = df_masses['Well'] + '-' + df_masses['IntervalNumber'].astype(str)
        df_masses['keep'] = True

        # Sensor:
        # sensor_dict = {}
        # df_sensor = xl_file.parse('Sensor', header=None).transpose()
        # # - The df needs to have two rows => key and value for the dict!
        # if df_sensor.shape[0] != 2:
        #     raise AssertionError(f'More than one column of parameters in the sheet "Sensor!"')
        # for col_idx in df_sensor.columns:
        #     sensor_dict[df_sensor.loc[0, col_idx]] = df_sensor.loc[1, col_idx]

        if verbose:
            print(f'...finished loading and parsing data!')

        return cls(run_name=run_name,
                   guid=guid,
                   input_xlsm_filename=input_xlsm_filename,
                   start_time_dt=start_time_dt,
                   end_time_dt=end_time_dt,
                   settings_dict=settings_dict,
                   df_panel_data=df_panel_data,
                   df_interval_analysis=df_interval_analysis,
                   df_masses=df_masses,
                   )

    def export_csv_files(self, output_filepath, sort_by_time=False, verbose=True):
        """Write CSV files to output directory

        Parameters
        ----------
        output_filepath : str
            Path to the output directory.
        sort_by_time : bool, optional (default=`False`)
            Sort data in the Masses CSV file by the observation time.
        verbose : bool, optional (default = `True`)
            If `True`, status messages are written to the command line.

        Returns
        -------
        :py:obj:`.LSData`
            Contains all LS output data loaded from the given xlsm file.

        """
        if verbose:
            print('Write output')

        # Checks:
        if not os.path.exists(output_filepath):
            raise AssertionError(f'The output path does not exist: {output_filepath}')
        self.output_dir_path = output_filepath

        if self.guid:
            filename_ending = f'{self.run_name}_{self.guid}.csv'
        else:
            filename_ending = f'{self.run_name}.csv'

        # Write PanelData:
        filename = os.path.join(output_filepath, f'Metadata_{filename_ending}')
        if verbose:
            print(f'Write PanelData to: {filename}')
        self.df_panel_data.to_csv(filename, index=False)

        # Write Masses:
        filename = os.path.join(output_filepath, f'Masses_{filename_ending}')
        if verbose:
            print(f'Write Masses to: {filename}')
        if sort_by_time:
            if verbose:
                print(f' - Sort Masses by Time.')
            self.df_masses.sort_values(by=['Time']).to_csv(filename, index=False)
        else:
            self.df_masses.to_csv(filename, index=False)

        # Write IntervalAnalysis:
        filename = os.path.join(output_filepath, f'SamplesSummary_{filename_ending}')
        if verbose:
            print(f'Write IntervalAnalysis to: {filename}')
        self.df_interval_analysis.to_csv(filename, index=False)

    def calc_sample_statistics(self, verbose=True, selection_only=False):
        """Calculate statistical values for each sample and add it to the self.df_interval_analysis."""
        if verbose & selection_only:
            print('Calculate sample statistics (selection only).')
        elif verbose:
            print('Calculate sample statistics.')

        for idx, row in self.df_interval_analysis.iterrows():
            # For all masses in a sample:
            if not selection_only:
                tmp_filter = (self.df_masses['Id'] == row.Id) & (self.df_masses['IntervalNumber'] == row.IntervalNumber)
                tmp_filter_1 = (self.df_interval_analysis['Id'] == row.Id) & \
                               (self.df_interval_analysis['IntervalNumber'] == row.IntervalNumber)
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_median'] = self.df_masses.loc[tmp_filter, 'Mass'].median()
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_std'] = self.df_masses.loc[tmp_filter, 'Mass'].std()
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q25'] = \
                    self.df_masses.loc[tmp_filter, 'Mass'].quantile(0.25)
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q75'] = \
                    self.df_masses.loc[tmp_filter, 'Mass'].quantile(0.75)
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_iqr'] = \
                    self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q75'] - \
                    self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q25']
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_rCV'] = \
                    74.1 * self.df_interval_analysis.loc[tmp_filter_1, 'Mass_iqr'] / \
                    self.df_interval_analysis.loc[tmp_filter_1, 'Mass_median']

            # For selected items only (flag `keep` = True):
            tmp_filter = (self.df_masses['Id'] == row.Id) & (self.df_masses['IntervalNumber'] == row.IntervalNumber) & (self.df_masses['keep'])
            tmp_filter_1 = (self.df_interval_analysis['Id'] == row.Id) & \
                           (self.df_interval_analysis['IntervalNumber'] == row.IntervalNumber)
            self.df_interval_analysis.loc[tmp_filter_1, 'Mass_median_keep'] = self.df_masses.loc[tmp_filter, 'Mass'].median()
            self.df_interval_analysis.loc[tmp_filter_1, 'Mass_mean_keep'] = self.df_masses.loc[tmp_filter, 'Mass'].mean()
            self.df_interval_analysis.loc[tmp_filter_1, 'Mass_std_keep'] = self.df_masses.loc[tmp_filter, 'Mass'].std()
            self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q25_keep'] = \
                self.df_masses.loc[tmp_filter, 'Mass'].quantile(0.25)
            self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q75_keep'] = \
                self.df_masses.loc[tmp_filter, 'Mass'].quantile(0.75)
            self.df_interval_analysis.loc[tmp_filter_1, 'Mass_iqr_keep'] = \
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q75_keep'] - \
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_q25_keep']
            self.df_interval_analysis.loc[tmp_filter_1, 'Mass_rCV_keep'] = \
                74.1 * self.df_interval_analysis.loc[tmp_filter_1, 'Mass_iqr_keep'] / \
                self.df_interval_analysis.loc[tmp_filter_1, 'Mass_median_keep']
            self.df_interval_analysis.loc[tmp_filter_1, 'DetectedParticles_keep'] = len(self.df_masses.loc[tmp_filter, 'Mass'])

    @property
    def get_number_of_observations(self):
        """Return the number of observations (items in the data series)."""
        if self.df_masses is not None:
            return len(self.df_masses)
        else:
            return 0

    @property
    def get_number_of_wells(self):
        """Return the number wells."""
        if self.df_panel_data is not None:
            return len(self.df_panel_data)
        else:
            return 0

    @property
    def get_number_of_intervals(self):
        """Return the number intervals."""
        if self.df_interval_analysis is not None:
            return len(self.df_interval_analysis)
        else:
            return 0

    @property
    def get_sample_ids(self):
        """Return list of IDs of all samples."""
        if self.df_interval_analysis is not None:
            return self.df_interval_analysis['SampleID'].to_list()
        else:
            return []

    def __str__(self):
        if self.run_name is not None:
            return f'Run "{self.run_name}" with {self.get_number_of_observations} observations in ' \
                   f'{self.get_number_of_intervals} intervals and {self.get_number_of_wells} wells. '
        else:
            return f'Not data available yet.'

    def flag_masses(self, min_mass: float, max_mass: float, sample_id: str, verbose=True):
        """Set the `keep` flag in the masses dataframe according to the data limits (min, max) and sample ID."""
        tmp_filter = self.df_masses['SampleID'] == sample_id
        self.df_masses.loc[tmp_filter, 'keep'] = (self.df_masses.loc[tmp_filter, 'Mass'] < max_mass) & (self.df_masses.loc[tmp_filter, 'Mass'] > min_mass)
        info_string = f'Sample {sample_id}: {len(self.df_masses.loc[~self.df_masses["keep"] & tmp_filter])} out of {len(self.df_masses.loc[tmp_filter])} masses deselected. {len(self.df_masses.loc[self.df_masses["keep"] & tmp_filter])} remaining.'

        # set thresholds in sample dataframe:
        tmp_filter = self.df_interval_analysis['SampleID'] == sample_id
        self.df_interval_analysis.loc[tmp_filter, 'keep_max_mass'] = max_mass
        self.df_interval_analysis.loc[tmp_filter, 'keep_min_mass'] = min_mass

        if verbose:
            print(info_string)
        return info_string

    def reset_flag_masses(self, sample_id: str, verbose=True):
        """Reset alls keep flags in the sample with the ID `sample_id`."""
        print(sample_id)
        tmp_filter = self.df_masses['SampleID'] == sample_id
        self.df_masses.loc[tmp_filter, 'keep'] = True
        tmp_filter = self.df_interval_analysis['SampleID'] == sample_id
        self.df_interval_analysis.loc[tmp_filter, 'keep_min_mass'] = None
        self.df_interval_analysis.loc[tmp_filter, 'keep_max_mass'] = None

def remove_space_from_column_names(df):
    """Removes white space from column names of input dataframe."""
    col_names = df.columns
    col_names_corrected = []
    for col_name in col_names:
        col_names_corrected.append(col_name.strip())
    df.columns = col_names_corrected
    return df


def row_to_list(row) -> list:
    """Convert dataframe row to list and remove all trailing NaN values."""
    item_not_nan_max_idx = row.loc[~row.isna()].index.max()
    if item_not_nan_max_idx is np.nan:  # No items that are not NaN!
        out_list = []
    else:
        out_list = row.loc[:item_not_nan_max_idx].to_list()
    return out_list


if __name__ == '__main__':
    """Main function, primarily for debugging and testing."""
    xlsm_filename = '../../data/Example_several_wells/Vibrio_starvation_24.11.22_221125_163425.xlsm'
    output_directory = '../../output/'

    ls_data = LSData.from_xlsm_file(input_xlsm_filename=xlsm_filename)
    ls_data.export_csv_files(output_directory)

    print('End')

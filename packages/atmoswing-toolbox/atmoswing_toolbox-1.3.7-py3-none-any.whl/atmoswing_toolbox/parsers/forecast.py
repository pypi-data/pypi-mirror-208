import os

import numpy as np
from netCDF4 import Dataset


class Forecast:
    """Extract AtmoSwing Forecaster outputs"""

    def __init__(self, file_path=''):
        self.file_path = file_path
        self.version = 0
        self.target_dates = None
        self.analog_criteria = None
        self.analog_dates = None
        self.analog_values = None
        self.analogs_nb = None
        self.stations_names = None
        self.stations_ids = None
        self.stations_heights = None
        self.stations_x_coords = None
        self.stations_y_coords = None
        self.reference_axis = None
        self.reference_values = None
        self._opened = False
        self._file = None
        self._use_analogs_nb_t0 = False

    def open(self):
        if not os.path.isfile(self.file_path):
            print(f'File {self.file_path} not found')
            return False

        # Read content
        self._file = Dataset(self.file_path, 'r')

        # Get version
        self.version = self._file.version_major + self._file.version_minor / 10

        # Extract variables
        if self.version <= 1.1:
            self.target_dates = self._file.variables['targetdates']
            self.analog_criteria = self._file.variables['analogscriteria']
            self.analog_dates = self._file.variables['analogsdates']
            self.analog_values = self._file.variables['analogsvaluesgross']
            self.analogs_nb = self._file.variables['analogsnb']
            self.stations_names = self._file.variables['stationsnames']
            self.stations_ids = self._file.variables['stationsids']
            self.stations_heights = self._file.variables['stationsheights']
            self.stations_x_coords = self._file.variables['loccoordu']
            self.stations_y_coords = self._file.variables['loccoordv']
            self.reference_axis = self._file.variables['returnperiods']
            self.reference_values = self._file.variables[
                'dailyprecipitationsforreturnperiods']
        elif self.version <= 1.2:
            self.target_dates = self._file.variables['target_dates']
            self.analog_criteria = self._file.variables['analogs_criteria']
            self.analog_dates = self._file.variables['analogs_dates']
            self.analog_values = self._file.variables['analogs_values_gross']
            self.analogs_nb = self._file.variables['analogs_nb']
            self.stations_names = self._file.variables['stations_names']
            self.stations_ids = self._file.variables['stations_ids']
            self.stations_heights = self._file.variables['stations_heights']
            self.stations_x_coords = self._file.variables['loc_coord_u']
            self.stations_y_coords = self._file.variables['loc_coord_v']
            self.reference_axis = self._file.variables['reference_axis']
            self.reference_values = self._file.variables['reference_values']
        else:
            self.target_dates = self._file.variables['target_dates']
            self.analog_criteria = self._file.variables['analog_criteria']
            self.analog_dates = self._file.variables['analog_dates']
            self.analog_values = self._file.variables['analog_values']
            self.analogs_nb = self._file.variables['analogs_nb']
            self.stations_names = self._file.variables['station_names']
            self.stations_ids = self._file.variables['station_ids']
            self.stations_heights = self._file.variables['station_heights']
            self.stations_x_coords = self._file.variables['station_x_coords']
            self.stations_y_coords = self._file.variables['station_y_coords']
            self.reference_axis = self._file.variables['reference_axis']
            self.reference_values = self._file.variables['reference_values']

        self._opened = True

        return True

    def close(self):
        self._check_opened()
        self._file.close()

    def _check_opened(self):
        if not self._opened:
            raise Exception(f'File {self.file_path} not opened')

    def use_analogs_nb_t0(self):
        self._use_analogs_nb_t0 = True

    def get_analogs_nb(self, time_lapse):
        self._check_opened()
        if self._use_analogs_nb_t0:
            return int(np.array(self.analogs_nb[:])[0])
        else:
            return int(np.array(self.analogs_nb[:])[time_lapse])

    def _get_station_index(self, station_id):
        self._check_opened()
        stations_ids = np.array(self.stations_ids[:])
        i_stat = np.where(stations_ids == station_id)
        if i_stat[0].size == 0:
            raise Exception(f'Station id {station_id} not found')

        return i_stat[0]

    def get_station_name(self, station_id):
        self._check_opened()
        i_stat = self._get_station_index(station_id)

        return self.stations_names[i_stat][0]

    def get_reference(self, station_id):
        self._check_opened()
        i_stat = self._get_station_index(station_id)

        ref_axis = np.array(self.reference_axis)
        all_ref_values = np.array(self.reference_values[:, :])
        if self.version < 1.2:
            curr_shape = all_ref_values.shape
            new_shape = curr_shape[::-1]
            all_ref_values = np.reshape(all_ref_values, new_shape)
            all_ref_values = np.transpose(all_ref_values)
            ref_values = all_ref_values[:, i_stat]
        else:
            ref_values = all_ref_values[i_stat, :][0]

        return {'axis': ref_axis, 'values': ref_values}

    def get_analog_values(self, station_id, time_lapse):
        self._check_opened()
        i_stat = self._get_station_index(station_id)

        analog_values = np.array(self.analog_values[:, :])
        if self.version < 1.2:
            curr_shape = analog_values.shape
            new_shape = curr_shape[::-1]
            analog_values = np.reshape(analog_values, new_shape)
            analog_values = np.transpose(analog_values)

        nb_analogs = self.get_analogs_nb(time_lapse)

        col_start = 0
        for i_lapse in np.arange(time_lapse):
            col_start = col_start + np.array(self.analogs_nb[:])[i_lapse]
        col_end = col_start + nb_analogs

        return analog_values[i_stat, col_start:col_end]

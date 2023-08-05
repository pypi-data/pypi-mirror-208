import glob
import os

import dateutil.parser
import numpy as np

import atmoswing_toolbox as astb
from atmoswing_toolbox.utils import mjd

from .predictor_dataset import PredictorDataset


class GribDataset(PredictorDataset):
    """Extract Grib data"""

    def __init__(self, directory, file_pattern):
        super().__init__(directory, file_pattern)
        self.grib_version = 0
        self.param_code_1 = []
        self.param_code_2 = []
        self.param_code_3 = []

        if not astb.has_eccodes:
            raise ImportError("eccodes is required to do this.")

    def load(self):
        try:
            self._list()
            self._extract()
        except OSError as err:
            print(f"OS error: {err}")
        except Exception as e:
            print("Unexpected error:", e)
            raise

    def _list(self):
        if not os.path.isdir(self.directory):
            raise Exception(f'Directory {self.directory} not found')

        self._files = glob.glob(os.path.join(self.directory, self.file_pattern))

        if len(self._files) == 0:
            raise Exception(
                f'No file found as {os.path.join(self.directory, self.file_pattern)}')

        self._files.sort()

    def _extract(self):
        for file in self._files:
            if not os.path.isfile(file):
                raise Exception(f'File {file} not found')

            print('Reading ' + file)

            f = open(file, 'rb')

            while True:
                msgid = astb.eccodes.codes_new_from_file(
                    f, astb.eccodes.CODES_PRODUCT_GRIB)

                if msgid is None:
                    break

                if self.grib_version == 0:
                    self.grib_version = astb.eccodes.codes_get_long(
                        msgid, "editionNumber")

                self._extract_axes(msgid)
                self._extract_level(msgid)
                self._extract_time(msgid)
                self._extract_grib_code(msgid)

                data = astb.eccodes.codes_get_array(msgid, "values")
                n_lats = len(self.axis_lat)
                n_lons = len(self.axis_lon)
                if len(self.data) == 0:
                    self.data = data.reshape((1, 1, n_lats, n_lons))
                else:
                    if self.data.shape[2] != n_lats or self.data.shape[3] != n_lons:
                        raise Exception("Issues in the size of the arrays.")
                    self.data = np.append(self.data,
                                          data.reshape((1, 1, n_lats, n_lons)),
                                          axis=0)

                units = astb.eccodes.codes_get(msgid, "units")
                if self.data_units is None:
                    self.data_units = units
                if self.data_units != units:
                    raise Exception("Only 1 type of data per file supported so far.")

                astb.eccodes.codes_release(msgid)

            f.close()

    def _extract_axes(self, msgid):
        n_lats = astb.eccodes.codes_get_long(msgid, "Nj")
        n_lons = astb.eccodes.codes_get_long(msgid, "Ni")
        lat_start = astb.eccodes.codes_get_long(
            msgid, "latitudeOfFirstGridPointInDegrees")
        lon_start = astb.eccodes.codes_get_long(
            msgid, "longitudeOfFirstGridPointInDegrees")
        lat_end = astb.eccodes.codes_get_long(
            msgid, "latitudeOfLastGridPointInDegrees")
        lon_end = astb.eccodes.codes_get_long(
            msgid, "longitudeOfLastGridPointInDegrees")
        if lon_end < lon_start:
            lon_start -= 360

        axis_lat = np.linspace(lat_start, lat_end, n_lats)
        axis_lon = np.linspace(lon_start, lon_end, n_lons)

        if len(self.axis_lat) == 0:
            self.axis_lat = axis_lat
            self.axis_lon = axis_lon
        else:
            if not np.array_equal(self.axis_lat, axis_lat):
                raise Exception("Only 1 extent per file is supported so far.")
            if not np.array_equal(self.axis_lon, axis_lon):
                raise Exception("Only 1 extent per file is supported so far.")

    def _extract_level(self, msgid):
        level = astb.eccodes.codes_get_double(msgid, "level")
        type = astb.eccodes.codes_get(msgid, "typeOfLevel")
        if type == "isobaricInPa":
            level /= 100

        if len(self.axis_level) == 0:
            self.axis_level.append(level)
        else:
            if self.axis_level[0] != level:
                raise Exception("Only 1 level per file is supported so far.")

    def _extract_time(self, msgid):
        ref_date = dateutil.parser.parse(
            astb.eccodes.codes_get_string(msgid, "dataDate"))
        ref_date_mjd = mjd.as_mjd(ref_date.year, ref_date.month, ref_date.day)
        ref_time = astb.eccodes.codes_get(msgid, "dataTime")

        forecast_time = 0
        if self.grib_version == 2:
            forecast_time = astb.eccodes.codes_get_double(msgid, "forecastTime")
        elif self.grib_version == 1:
            forecast_time = astb.eccodes.codes_get_double(msgid, "endStep")

        time_unit = astb.eccodes.codes_get_long(msgid, "stepUnits")
        if time_unit == 0:
            forecast_time /= 1440
        elif time_unit == 1:
            forecast_time /= 24

        time = ref_date_mjd + ref_time / 24 + forecast_time

        self.axis_time.append(time)

    def _extract_grib_code(self, msgid):
        discipline = 0
        category = 0
        number = 0
        if self.grib_version == 2:
            discipline = astb.eccodes.codes_get_long(msgid, "discipline")
            category = astb.eccodes.codes_get_long(msgid, "parameterCategory")
            number = astb.eccodes.codes_get_long(msgid, "parameterNumber")
        elif self.grib_version == 1:
            category = astb.eccodes.codes_get_long(msgid, "table2Version")
            number = astb.eccodes.codes_get_long(msgid, "indicatorOfParameter")

        self.param_code_1.append(discipline)
        self.param_code_2.append(category)
        self.param_code_3.append(number)

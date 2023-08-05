import os

from netCDF4 import Dataset

NETCDF_3 = 0
""" NetCDF 3 format - larger but faster """
NETCDF_4 = 1
""" NetCDF 4 format - smaller but longer to read """


class GenericDataset:
    """Generic dataset"""

    def __init__(self, directory, var_name, ref_data):
        self.directory = directory
        self.var_name = var_name
        self.ref_data = ref_data
        if not os.path.exists(directory):
            os.makedirs(directory)

    def generate(self, format=NETCDF_3, file_name=None):
        shape = self.ref_data.data.shape  # time, level, lat, lon

        if file_name is None:
            file_name = self.var_name + '.nc'
        file_path = os.path.join(self.directory, file_name)
        if format == NETCDF_3:
            nc = Dataset(file_path, "w", format="NETCDF3_CLASSIC")
        else:
            nc = Dataset(file_path, "w", format="NETCDF4")

        # Global attributes
        nc.standardized = 0
        if self.ref_data.is_standardized:
            nc.standardization_mean = self.ref_data.mean
            nc.standardization_sd = self.ref_data.sd

        # Dimensions
        nc.createDimension("time", shape[0])
        nc.createDimension("level", shape[1])
        nc.createDimension("lat", shape[2])
        nc.createDimension("lon", shape[3])

        # Variables
        var_level = nc.createVariable("level", "f4", ("level",))
        var_lat = nc.createVariable("lat", "f4", ("lat",))
        var_lon = nc.createVariable("lon", "f4", ("lon",))
        if format == NETCDF_3:
            var_time = nc.createVariable("time", "f4", ("time",))
            var_data = nc.createVariable(self.var_name, "f4",
                                         ("time", "level", "lat", "lon",))
        else:
            var_time = nc.createVariable("time", "f4", ("time",),
                                         zlib=True, complevel=6,
                                         least_significant_digit=4)
            var_data = nc.createVariable(self.var_name, "f4",
                                         ("time", "level", "lat", "lon",),
                                         zlib=True, complevel=6)

        # Attributes
        var_time.setncattr('name', 'time')
        var_time.long_name = 'time'
        var_time.units = 'days since 1858-11-17 00:00:00.0 +0:00'
        var_time.calendar = 'standard'
        var_lat.setncattr('name', 'lat')
        var_lat.long_name = 'latitude'
        var_lat.units = 'degree_north'
        var_lon.setncattr('name', 'lon')
        var_lon.long_name = 'longitude'
        var_lon.units = 'degree_east'
        var_data.units = self.ref_data.data_units

        # Set data
        var_time[:] = self.ref_data.axis_time
        var_level[:] = self.ref_data.axis_level
        var_lat[:] = self.ref_data.axis_lat
        var_lon[:] = self.ref_data.axis_lon
        var_data[:] = self.ref_data.data

        nc.close()

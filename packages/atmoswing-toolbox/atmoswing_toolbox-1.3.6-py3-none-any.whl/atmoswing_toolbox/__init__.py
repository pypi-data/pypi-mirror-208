try:
    from netCDF4 import Dataset
except ImportError:
    has_netcdf = False
else:
    has_netcdf = True

try:
    import eccodes
except ImportError:
    has_eccodes = False
else:
    has_eccodes = True

__all__ = ('Dataset', 'eccodes', 'has_netcdf', 'has_eccodes')

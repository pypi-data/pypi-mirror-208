from xarray import DataArray
from .plot_folium import plot_folium
setattr(DataArray, 'plot_folium', plot_folium)
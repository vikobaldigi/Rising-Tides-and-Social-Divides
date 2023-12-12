# %%
# Imports
from pathlib import Path
from IPython.core.display import Video

import numpy as np
import pandas as pd
import geopandas as gpd  # Vector data handling
import osmnx as ox       # Downloading data from OSM

from shapely.geometry import box
from scipy.spatial import cKDTree as KDTree # For Inverse Distance Weight calculation

import xarray as xr    
import xrspatial    # Hillshading
import rioxarray    # Working with geospatial data in xarray

import matplotlib.pyplot as plt
from datashader.transfer_functions import shade, stack

import geojson

# %%
# DEM File Retrevived from the USGS LidarExplorer
dem = rioxarray.open_rasterio('/Users/vikobal/Documents/Vi Kobal/PythonProjects/USGS_one_meter_x59y452_NY_CMPG_2013.tif')

# %%
# Make DEM smaller and clip to focus area
# Coordinates retreived from https://boundingbox.klokantech.com/
geom = '''{"type": "Polygon",
                "coordinates":[[
                    [-73.9418564389,40.7327728479],
                    [-73.7950013339,40.7327728479],
                    [-73.7950013339,40.8422825913],
                    [-73.9418564389,40.8422825913],
                    [-73.9418564389,40.7327728479]]]}'''

# %%
cropping_geometries = [geojson.loads(geom)]
cropped = dem.rio.clip(geometries=cropping_geometries, crs=4326)

# %%
cropped = cropped.coarsen(x=3, boundary='trim').mean().coarsen(y=3, boundary='trim').mean()

# %%
# Plot Digital Elevation Model (DEM)
cropped.squeeze().plot.imshow()

# %%
# fetch coordinates for the East River
river = ox.geocode_to_gdf('East River', which_result=1)
river = river.to_crs(cropped.rio.crs)

# %%
# plot the river
river.plot()

# %%
# Combining river and DEM geometries
# cut to area of interest
cropped.rio.bounds()

# %%
bounds = cropped.rio.bounds()
xmin, ymin, xmax, ymax = bounds

# %%
river = river.clip(bounds)

# %%
# Plot river path in reference to DEM
river_geom = river.geometry.iloc[0]
river_geom

# %%
# plotting river and DEM together
cropped = cropped.sel(y=slice(ymax, ymin), x=slice(xmin, xmax))

# %%
fig, ax = plt.subplots()
cropped.squeeze().plot.imshow(ax=ax)
river.plot(ax=ax, color='red')

# %%
# Import to Calculate Relative Elevation Model (REM)
import shapely      

# %%
def split_coords(geom):
    x = []
    y = []
    for i in shapely.get_coordinates(geom):
        x.append(i[0])
        y.append(i[1])
    return x, y

# %%
# Extract coordinates as `DataArray`
xs, ys = split_coords(river_geom)
xs, ys = xr.DataArray(xs, dims='z'), xr.DataArray(ys, dims='z')

# %%
sampled = cropped.interp(x=xs, y=ys, method='nearest').dropna(dim='z')

# %%
#  Interpolate the sampled elevation values to create a 2D elevation raster
# Sampled river coordinates
c_sampled = np.vstack([sampled.coords[c].values for c in ('x', 'y')]).T

# All (x, y) coordinates of the original DEM
c_x, c_y = [cropped.coords[c].values for c in ('x', 'y')]
c_interpolate = np.dstack(np.meshgrid(c_x, c_y)).reshape(-1, 2)

# Sampled values
values = sampled.values.ravel()

# %%
c_interpolate

# %%
# Perform the interpolation
tree = KDTree(c_sampled)
tree

# %%
# Subtract the interpolated elevation raster from the DEM
# IWD interpolation (test out to determine k value)
distances, indices = tree.query(c_interpolate, k=11)

weights = 1 / distances
weights = weights / weights.sum(axis=1).reshape(-1, 1)

interpolated_values = (weights * values[indices]).sum(axis=1)

# %%
interpolated_values

# %%
# We create a `DataArray` out of the inerpolated values
elevation_raster = xr.DataArray(
    interpolated_values.reshape((len(c_y), len(c_x))).T, dims=('x', 'y'), coords={'x': c_x, 'y': c_y}
)

# %%
fig, ax = plt.subplots()
elevation_raster.transpose().plot.imshow(ax=ax)
river.plot(ax=ax, color='red')

# %%
# prepare visualizations
rem = cropped - elevation_raster

# %%
# using colors to make flood map look like an x-ray
colors = ['#f2f7fb', '#81a8cb', '#37123d']

# %%
shade(rem.squeeze(), cmap=colors, span=[0, 10], how='linear')

# %%
# Visualize the DEM along with the REM
a = shade(xrspatial.hillshade(cropped.squeeze(), angle_altitude=1, azimuth=310), cmap=['black', 'white'], how='linear')
b = shade(rem.squeeze(), cmap=colors, span=[0, 10], how='linear', alpha=200)
stack(a, b)



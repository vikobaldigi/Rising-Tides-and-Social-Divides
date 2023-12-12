# %%
# Import packages
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['savefig.facecolor'] = 'white'
%matplotlib inline

# %%
# Check package versions
%reload_ext watermark
%watermark -v -p numpy,pandas,seaborn,matplotlib,geopandas

# %%
# Read in data
# Source: https://data.cityofnewyork.us/City-Government/NYC-Stormwater-Flood-Map-Extreme-Flood-with-2080-S/w8eg-8ha6
gdf = gpd.read_file('/Users/vikobal/Documents/Vi Kobal/PythonProjects/stormwater-data.zip')

# sanity checks
print('shape: {}'.format(gdf.shape))
print('crs: {}'.format(gdf.crs))

# preview data
gdf.head()

# %%
# summary statistics of flood polygons
(gdf
 .groupby(by='flood_classification')[['flood_classification']]
 .count()
 .rename(columns={'flood_classification':'count_polygons'})
)

# %%
# summary statistics of flood polygons
acres_conversion = 43560

(gdf
 .groupby(by='flood_classification')[['Shape_Area']]
 .sum()
 .div(acres_conversion)
 .round(0)
 .astype(int)
 .rename(columns={'Shape_Area':'shape_area_acres'})
 .reset_index()
)

# %%
# Queens Flood Plain Spatial Analysis
# importing borough boundaries
path = 'https://data.cityofnewyork.us/api/geospatial/tqmj-j8zm?method=export&format=Shapefile'
borough_gdf = gpd.read_file(path)

# preview data
print('shape of data: {}'.format(borough_gdf.shape))
borough_gdf.head()

# %%
# examine crs
borough_gdf.crs

# %%
# transform crs
borough_gdf = borough_gdf.to_crs(2263)

borough_gdf.crs

# %%
# Plot of NYC borough boundaries
borough_gdf.plot()
plt.title('NYC Borough Boundaries')

# %%
# Creating the Stormwater Flood Map for all flood classifications
fig, ax = plt.subplots(figsize=(8, 8))

patches = []
colors = ['tab:cyan', 'blue', 'tab:orange']
classifications = gdf['flood_classification'].unique()

for label, color in zip(classifications, colors):
    
    (gdf
     .loc[gdf['flood_classification'].isin([label])]
     .plot(color=color, ax=ax)
    )
    
    patches.append(mpatches.Patch(color=color, label=label))

# Outlines Queens   
borough_gdf[borough_gdf['boro_name'] == 'Queens'].plot(
    ax=ax, 
    facecolor='none', 
    edgecolor='black', 
    zorder=1
)

plt.legend(
    title='', 
    handles=patches, 
    fontsize='12', 
    loc=2
) 

plt.axis('off')
plt.tight_layout()

# %%
# Filter the borough data for Queens
mask = borough_gdf.loc[borough_gdf['boro_name'] == 'Queens']

# Add 0 buffer to flood polygon geometry to use clip method
gdf['geometry'] = gdf['geometry'].buffer(0)

# Clip flood polygon against Queens' geometry
clipped_gdf = gpd.clip(gdf, mask)
clipped_gdf['boro'] = 'Queens'  # Add the borough name

# Calculate area and length
clipped_gdf['Shape_Area'] = clipped_gdf.area
clipped_gdf['Shape_Length'] = clipped_gdf.length

# Preview data
print('Shape of data: {}'.format(clipped_gdf.shape))
clipped_gdf.head()

# %%
boros = ['Queens']  # Include only Queens County

classification = 'Deep and Contiguous Flooding'

for boro in boros: 
    fig, ax = plt.subplots(figsize=(12, 12))
    
    (clipped_gdf
     .loc[
         (clipped_gdf['flood_classification'] == classification)
         & (clipped_gdf['boro'] == boro)]  # Change 'isin' to '=='
     .plot(ax=ax)
    )

    (borough_gdf
     .loc[borough_gdf['boro_name'] == boro]
     .plot(ax=ax, facecolor='none', edgecolor='black', zorder=1)
    )

    plt.axis('off')   
    plt.tight_layout()

# %%
# Examine Clipped Future High Tides 2080
classification = 'Future High Tides 2080'
boro = 'Queens'  # Specify Queens County directly

fig, ax = plt.subplots(figsize=(12, 12))

(clipped_gdf
 .loc[
     (clipped_gdf['flood_classification'] == classification)
     & (clipped_gdf['boro'] == boro)]  # Change 'isin' to '=='
 .plot(ax=ax)
)

(borough_gdf
 .loc[borough_gdf['boro_name'] == boro]
 .plot(ax=ax, facecolor='none', edgecolor='black', zorder=1)
)

plt.axis('off')
plt.tight_layout()



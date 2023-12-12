# %%
# Import modules
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from census import Census
from us import states
import os

# %%
# Set API key
c = Census("INSERT KEY HERE")

# %%
# Obtain Census variables from the 2022 ACS at the tract level for Queens County, NY (FIPS code: 081)
# C17002_001E: count of ratio of income to poverty in the past 12 months (total)
# C17002_002E: count of ratio of income to poverty in the past 12 months (< 0.50)
# C17002_003E: count of ratio of income to poverty in the past 12 months (0.50 - 0.99)
# B01003_001E: total population
# Sources: https://api.census.gov/data/2022/acs/acs5/variables.html; https://pypi.org/project/census/
qn_census = c.acs5.state_county_tract(fields = ('NAME', 'B03002_001E', 'B03002_003E', 'B03002_004E', 'B03002_005E', 'B03002_006E', 'B03002_012E'),
                                      state_fips = states.NY.fips,
                                      county_fips = "081",
                                      tract = "*",
                                      year = 2021)

# %%
# Create a dataframe from the census data
qn_df = pd.DataFrame(qn_census)

# %%
# Show the dataframe
print(qn_df.head(2))
print('Shape: ', qn_df.shape)

# %%
# Access shapefile of Queens census tracts
qn_tract = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_36_tract.zip")

# Reproject shapefile to UTM Zone NAD83
# https://www.spatialreference.org/ref/epsg/nad83-new-york-long-island-ftus/
qn_tract = qn_tract.to_crs(epsg = 32118)

# Print GeoDataFrame of shapefile
print(qn_tract.head(2))
print('Shape: ', qn_tract.shape)

# Check shapefile projection
print("\nThe shapefile projection is: {}".format(qn_tract.crs))

# %%
# Combine state, county, and tract columns together to create a new string and assign to new column
qn_df["GEOID"] = qn_df["state"] + qn_df["county"] + qn_df["tract"]

# %%
# Print head of dataframe
qn_df.head(2)

# %%
# Remove columns
qn_df = qn_df.drop(columns = ["state", "county", "tract"])

# Show updated dataframe
qn_df.head(2)

# %%
# Check column data types for census data
print("Column data types for census data:\n{}".format(qn_df.dtypes))

# Check column data types for census shapefile
print("\nColumn data types for census shapefile:\n{}".format(qn_tract.dtypes))

# Source: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dtypes.html

# %%
# Join the attributes of the dataframes together
# Source: https://geopandas.org/docs/user_guide/mergingdata.html
qn_merge = qn_tract.merge(qn_df, on = "GEOID")

# Show result
print(qn_merge.head(2))
print('Shape: ', qn_merge.shape)

# %%
# Create new dataframe from select columns
qn_race_tract = qn_merge[["STATEFP", 
                          "COUNTYFP", 
                          "TRACTCE", 
                          "GEOID", "geometry", 
                          'B03002_001E', 
                          'B03002_003E', 
                          'B03002_004E', 
                          'B03002_005E', 
                          'B03002_006E', 
                          'B03002_012E']]

# Show dataframe
print(qn_race_tract.head(2))
print('Shape: ', qn_race_tract.shape)

# %%
# Save the DataFrame to a CSV file
qn_race_tract.to_csv('/Users/vikobal/Documents/Vi Kobal/PythonProjects/QueensDataProfile3.csv', index=False)

# %%
# Calculate the percentage of each race and store the values in new columns
# Example: qn_race_tract["White_Percentage"] = (qn_race_tract["B02001_002E"] / qn_race_tract["B02001_001E"]) * 100
# Calculate the percentage for each race category and store the values in new columns

# Calculate the percentage of each race and store the values in new columns using .loc
qn_race_tract.loc[:, 'White_Percentage'] = (qn_race_tract['B03002_003E'] / qn_race_tract['B03002_001E']) * 100
qn_race_tract.loc[:, 'Black_Percentage'] = (qn_race_tract['B03002_004E'] / qn_race_tract['B03002_001E']) * 100
qn_race_tract.loc[:, 'American_Indian_Percentage'] = (qn_race_tract['B03002_005E'] / qn_race_tract['B03002_001E']) * 100
qn_race_tract.loc[:, 'Asian_Percentage'] = (qn_race_tract['B03002_006E'] / qn_race_tract['B03002_001E']) * 100
qn_race_tract.loc[:, 'Hispanic_Percentage'] = (qn_race_tract['B03002_012E'] / qn_race_tract['B03002_001E']) * 100

# Display the updated DataFrame
# Drop rows with missing values
qn_race_tract = qn_race_tract.dropna()
print(qn_race_tract)

# %%
# Create the choropleth map
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
qn_race_tract.plot(column='White_Percentage', cmap='Blues', legend=False, ax=ax)

# Show the plot
plt.axis('off')
plt.tight_layout()
plt.show()

# %%
# Create the choropleth map
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
qn_race_tract.plot(column='Black_Percentage', cmap='Purples', legend=False, ax=ax)

# Show the plot
plt.axis('off')
plt.tight_layout()
plt.show()

# %%
# Create the choropleth map
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
qn_race_tract.plot(column='Asian_Percentage', cmap='Oranges', legend=False, ax=ax)

# Show the plot
plt.axis('off')
plt.tight_layout()
plt.show()

# %%
# Create the choropleth map
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
qn_race_tract.plot(column='Hispanic_Percentage', cmap='Reds', legend=False, ax=ax)

# Show the plot
plt.axis('off')
plt.tight_layout()
plt.show()

# %%
# Obtain median income data for Queens County, NY
# B19013_001E: Median household income in the past 12 months (in 2022 inflation-adjusted dollars)
median_income_data = c.acs5.state_county_tract(
    ("NAME", "B19013_001E"), 
    states.NY.fips, 
    county_fips="081", 
    tract="*",
    year=2021
)
# Create a dataframe from the census data
median_income_df = pd.DataFrame(median_income_data)

# Save the DataFrame to a CSV file
median_income_df.to_csv('/Users/vikobal/Documents/Vi Kobal/PythonProjects/QueensDataProfile6.csv', index=False)

# %%
# Sort the data in ascending order based on the B19013_001E column
median_income_df = median_income_df.sort_values("B19013_001E")

# Delete any rows containing the value -666666666.0 in the B19013_001E column
median_income_df = median_income_df[median_income_df["B19013_001E"] != -666666666.0]

# Show the sorted and filtered DataFrame
print(median_income_df)

# %%
# Access shapefile of Queens census tracts
qn_tract = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_36_tract.zip")

# Reproject shapefile to UTM Zone NAD83
qn_tract = qn_tract.to_crs(epsg=32118)

# Combine state, county, and tract columns together to create a new string and assign to new column
median_income_df["GEOID"] = median_income_df["state"] + median_income_df["county"] + median_income_df["tract"]

# Join the attributes of the dataframes together
qn_merge = qn_tract.merge(median_income_df, on="GEOID")

# Create subplots
fig, ax = plt.subplots(1, 1, figsize=(20, 10))

# Plot data
qn_merge.plot(column="B19013_001E", ax=ax, cmap="YlGn", legend=False)

# Remove the grid
ax.grid(False)

# Set the background color to white
ax.set_facecolor('white')

# Show the plot
plt.axis('off')
plt.tight_layout()
plt.show()



import pandas as pd  # provides interface for interacting with tabular data
import geopandas as gpd  # combines the capabilities of pandas and shapely for geospatial operations
from shapely.geometry import Point, Polygon, MultiPolygon  # for manipulating text data into geospatial shapes
from shapely import wkt  # stands for "well known text," allows for interchange across GIS programs
import rtree  # supports geospatial join
import os
import fnmatch
import matplotlib.pyplot as plt
import descartes
import numpy as np
import sys

##user-input:
home_dir = '/Users/saraprice/Documents/NYU/Fall_2020/DS_GA_1001/final_project'
sys.path.append(os.path.join(home_dir, 'wildfires-1001/code/functions/'))

#import user-defined functions
from gis_processing import *


'''
Step 1
------
Load relevant dataframes:
    1. USA boundaries (needed for state of CA boundary line)
    2. CA county data
'''
data_dir = os.path.join(home_dir, 'wildfires-1001/data')

#State boundaries
state_boundaries = gpd.read_file(os.path.join(data_dir, 'raw_data/state_boundaries_gis', 'tl_2017_us_state.dbf'))

#limit to California (so gdf will have 1 row)
ca_boundary = gpd.GeoDataFrame(state_boundaries[state_boundaries['NAME']== 'California'].geometry)
ca_boundary = ca_boundary.to_crs("EPSG:3857")

#Output cleaned CA boundary .shp file
ca_boundary.to_file(os.path.join(data_dir, 'clean_data/CA_boundary/CA_boundary.shp'))

#County boundaries
county_boundaries = gpd.read_file(os.path.join(data_dir, 'raw_data/counties_gis/CA_Counties_TIGER2016.shp'))

#Limit to just columns we're interested in
CA_counties = county_boundaries[['NAME', 'COUNTYFP', 'GEOID', 'ALAND', 'AWATER', 'geometry']]
#sum ALAND (land area) and AWATER (water area) to get the total area for each county
CA_counties['COUNTY_AREA'] = CA_counties.geometry.area

'''
Step 2
------
Generate grid across all counties
'''
#Generate grid over min and max x,y coordinates for CA counties
grid = generate_grid(CA_counties.geometry, 83000, 83000)
## Note that 83,000 has the len and width was arrived at through some testing

#Project grid onto CA state boundary line - not that this will result in not all new grid sections (i.e. those on the edges) being
#the same size
new_grid = gpd.overlay(ca_boundary, grid, how = 'intersection')

#Calculate area and proportion of total area of grid new region overlaid on CA boundary
new_grid['GRID_AREA'] = new_grid.geometry.area

#remove grid sections that are not above a certain quantile for the area - removes neglibly small new sections
min_area = np.quantile(new_grid['GRID_AREA'], 0.15)
new_grid_trimmed = new_grid[new_grid['GRID_AREA']>min_area]

#Add grid_id for numbering different grid sections 
new_grid_trimmed['GRID_ID'] = pd.Series(range(len(new_grid_trimmed)))

'''
Step 3
------
Assign counties to new grid sections based on which county in each grid square makes up the majority area (this is how we will map features that are associated with counties to each grid square)
'''
#Overlay the grid projected onto CA's map with county geometries
county_grid = gpd.overlay(CA_counties, new_grid_trimmed,  how = 'intersection')
county_grid['COUNTY_GRID_OVLP_AREA'] = county_grid.geometry.area
county_grid['COUNTY_GRID_OVLP_PROP'] = county_grid['COUNTY_GRID_OVLP_AREA']/county_grid['COUNTY_AREA']

#Group by grid id to find the county with the majority area in each grid section
county_grid_grp = county_grid[['GRID_ID', 'COUNTY_GRID_OVLP_PROP']].groupby('GRID_ID').max().reset_index()

#Merge back on full dataset to get the county ID information we want to append to grid data
county_grid2 = county_grid.merge(county_grid_grp, on = ['GRID_ID', 'COUNTY_GRID_OVLP_PROP'])
county_grid_fin = county_grid2[['NAME', 'COUNTYFP', 'GRID_ID', 'COUNTY_GRID_OVLP_PROP']]

#Merge county data onto new_grid_trimmed - this way we have county features but we have the grid geometry so this dataframe can be mapped to GIS data or regular pandas dataframes
print("# records in new_grid_trimmed: {}".format(len(new_grid_trimmed)))
print("# records in county grid df: {}".format(len(county_grid_fin)))
output_grid = new_grid_trimmed.merge(county_grid_fin, on = 'GRID_ID')
print("# records in output_grid df: {}".format(len(output_grid)))
output_grid.to_file(os.path.join(data_dir, 'clean_data/county_grid/county_grid.dbf'))


    
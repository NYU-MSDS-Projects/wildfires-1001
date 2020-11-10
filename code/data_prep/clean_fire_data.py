import pandas as pd  # provides interface for interacting with tabular data
import geopandas as gpd  # combines the capabilities of pandas and shapely for geospatial operations
from shapely.geometry import Point, Polygon, MultiPolygon  # for manipulating text data into geospatial shapes
from shapely import wkt  # stands for "well known text," allows for interchange across GIS programs
import rtree  # supports geospatial join
import os
import fnmatch
import numpy as np
from datetime import datetime as dt

'''
Keys for fire_gis tables:
    - a000000af = main historical fire data
'''

'''
User input params
-----------------
Below we'll set parameters for cutoffs and other decisions we make in data processing/ cleaning
'''
min_year = 1990
#Load fire data
home_dir = '/Users/saraprice/Documents/NYU/Fall_2020/DS_GA_1001/final_project'

#There are multiple possible files we want to use, so loop through all files with the desired ext (.gdbtable) and read those into dictionary
fire_gdb = {}
for file in os.listdir(os.path.join(home_dir, 'wildfires-1001/data/raw_data/fire_gis.gdb')):
    if fnmatch.fnmatch(file, '*.gdbtable'):
        key = str.replace(file, '.gdbtable', '')
        fire_gdb[key] = gpd.read_file(os.path.join(os.path.join(home_dir, 'wildfires-1001/data/raw_data/fire_gis.gdb', fire)))

        
'''
Step 1
------
Clean fire data fields
'''
fire_data = fire_gdb['a000000af']
fire_data = fire_data.to_crs('EPSG:3857')
print("Starting fire_data shape: {}".format(fire_data.shape))

#Drop rows where key columns (YEAR, CONT_DATE, ALARM_DATE, etc) are null
fire_data = fire_data.dropna(subset = ['YEAR_', 'ALARM_DATE', 'CONT_DATE'], axis = 0)
print("fire_data shape after removing NaNs in key fields: {}".format(fire_data.shape))

#Convert ALARM_DATE and CONT_DATE to datetime objects rather than strings
fire_data[['ALARM_DATE', 'CONT_DATE']] = fire_data[['ALARM_DATE', 'CONT_DATE']].astype(str).apply(lambda x: x[:str.find(x,'T')])
fire_data[['ALARM_DATE', 'CONT_DATE']] = pd.to_datetime(fire_data[['ALARM_DATE', 'CONT_DATE']], format = '%Y-%m-%d', \
                                                        errors = 'coerce')
'''
Create fire_key (unique identifier for fires which is a string of FIRE_NAME + YEAR + INC_NUM (incident number) + FIRE_NUM
FIRE_NUM and INC_NUM are different identifiers likely from different agencies in CA that are responsible for tracking fires
The reason we include both is that sometimes one is populated when the other isn't

By far FIRE_NAME is the least sparse field while INC_NUM and FIRE_NUM both have NAs. When INC_NUM and FIRE_NUM have NAs we replace with placeholdser 'NI' and 'NF' respectively - this is so we can tell which part of the key is missing or not (the incident numbers and fire numbers can be hard to tell apart).

There are only 4 fires without a name, and for those we leave an empty string. Because name is first in the key, these will start with _
'''
#Cleaning up NaNs in inc_num and fire_num
fire_data['INC_NUM'] = np.where(fire_data['INC_NUM'].isna() == True, 'NI', \
                                  np.where(fire_data['INC_NUM']=='00000000', 'NI', fire_data['INC_NUM']))
fire_data['FIRE_NUM'] = np.where(fire_data['FIRE_NUM'].isna() == True, 'NF', \
                                  np.where(fire_data['FIRE_NUM']=='000000000', 'NF', fire_data['FIRE_NUM']))

fire_data['FIRE_NAME'] = np.where(fire_data['FIRE_NAME'].isna() == True, '', fire_data['FIRE_NAME'])

fire_data['FIRE_KEY'] = fire_data['FIRE_NAME'].apply(lambda x: str.replace(x, ' ', '')) +'_'+ fire_data['YEAR_'] +'_'+\
                        fire_data['INC_NUM'] +'_'+ fire_data1['FIRE_NUM']

#Convert YEAR_ from object to int and save as YEAR. Also remove any records where YEAR = NA
fire_data = fire_data[fire_data['YEAR_']!='']
fire_data = fire_data.dropna(subset = ['YEAR_'], axis = 0)
fire_data['YEAR'] = fire_data['YEAR_'].astype(str).astype(int)
fire_data = fire_data[fire_data['YEAR']>=min_year]
print("fire_data shape after limiting to year >= {}: {}".format(min_year, fire_data.shape))

#Drop rows we don't need (keeping a bunch bc not sure what will be useful - need to do some more research
fire_data.drop_cols(['UNIT_ID', 'YEAR_', 'STATE', 'COMMENTS'], axis = 1, inplace = True)



                                      
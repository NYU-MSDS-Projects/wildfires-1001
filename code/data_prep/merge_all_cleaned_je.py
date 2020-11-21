#!/usr/bin/env python
# coding: utf-8

# # Pull in the main fire dataframe

# In[1]:


#import packages
import pandas as pd  # provides interface for interacting with tabular data
import geopandas as gpd  # combines the capabilities of pandas and shapely for geospatial operations
import rtree  # supports geospatial join
import os
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
import sys
import pickle
from shapely.ops import nearest_points
from datetime import datetime as dt, date
sys.path.append('/Users/jackepstein/Documents/GitHub/wildfires-1001/code/functions/')
data_dir = '/Users/jackepstein/Documents/GitHub/wildfires-1001/data'


# In[2]:


#read in the target variables for fire
target_df = {}
full_target_data = gpd.GeoDataFrame()
for i in np.arange(1, 4):
    target_df[i] = pd.read_pickle(os.path.join(data_dir, f'clean_data/target_full_{i}.pkl')) 
    full_target_data = full_target_data.append(target_df[i])
    
#change data types
full_target_data['COUNTYFP'] = full_target_data['COUNTYFP'].astype(int)
full_target_data['GRID_ID'] = full_target_data['GRID_ID'].astype(int)
full_target_data['YEAR'] = full_target_data['date'].apply(lambda x:x.year)  
full_target_data['MONTH'] = full_target_data['date'].apply(lambda x:x.month)  

#drop unneeded columns
full_target_data2 = full_target_data.drop(columns=['date','month_start', 'month_end', 'week_id',
                                                  'week_start', 'week_end', 'start_date', 'end_date'])


# In[ ]:


#checking what one instance will look like
#full_target_data2.loc[full_target_data2['GRID_ID']==36].loc[full_target_data2['month_id']=='2018_11']


# # Initial Group By

# In[3]:


#group by gridid and month and take means of fire data
#y_bin, y_fire_class_size -- take max
#y_fire_count -- count distinct of FIRE ID
#y_fire_area prop -- done below with a separate dissolve and join rather than groupby 
target_data_month = full_target_data2.groupby(['GRID_ID','month_id','YEAR', 'MONTH','COUNTYFP','NAME', 'GRID_AREA', 
                                               'COUNTY_ARE']).agg({'Y_bin':'max', 
                                                                   'Y_fire_class_size': 'max',
                                                                   'FIRE_KEY':'nunique'}).reset_index()
target_data_month = target_data_month.rename(columns={'FIRE_KEY': 'Y_fire_count'})


# In[4]:


#DO NOT RE-RUN VERY SLOW
#make a new DF with just needed columns
sub_geo_df = full_target_data2[['month_id', 'GRID_ID', 'geometry']]
#sub_geo_df.loc[sub_geo_df['GRID_ID']==36].loc[sub_geo_df['month_id']=='2018_11']

#only positive instances
sub_geo_df_2 = sub_geo_df.loc[~sub_geo_df['geometry'].isna()]

#dissolve
sub_geo_dissolve = sub_geo_df_2.dissolve(by=['GRID_ID','month_id'])


# In[5]:


#reset the index and calcuate area
sub_geo_dissolve = sub_geo_dissolve.reset_index()
sub_geo_dissolve['Fire_area'] = sub_geo_dissolve['geometry'].area


# In[6]:


#merge grouped by df with dissolved df
target_data_month = target_data_month.merge(sub_geo_dissolve, on=['GRID_ID','month_id'], how='left')
#replace NaN in Fire_area with 0
target_data_month['Fire_area'] = target_data_month['Fire_area'].fillna(0)


# In[9]:


target_data_month['Y_fire_area_prop'] = target_data_month['Fire_area']/target_data_month['GRID_AREA']


# In[10]:


#drop grid ID 59 -- no weather data
target_data_month_df = target_data_month.loc[target_data_month['GRID_ID']!=59]
#check for positive instances
#target_data_month_df.loc[target_data_month_df['Y_bin']==1]


# In[11]:


#take in an object formatted as YYYY_MM
def add_one_month(month_id_obj):
    
    #turn this object into a string
    #split this and take the element after the '_'
    #turn this back into an int
    month_int = int(str(month_id_obj).split('_')[1])
    year_int = int(str(month_id_obj).split('_')[0])
    
    #check if the month is decemember -- if so, set to 1 if not, add one
    if month_int == 12:
        mont = 1
        new_month_id = str(year_int+1)+'_'+str(mont)
    else:
        mont = int(month_int+1)
        new_month_id = str(year_int)+'_'+str(mont)
        
    return new_month_id    
    
#take in an object formatted as YYYY_MM
def sub_one_month(month_id_obj):
    
    #turn this object into a string
    #split this and take the element after the '_'
    #turn this back into an int
    month_int = int(str(month_id_obj).split('_')[1])
    year_int = int(str(month_id_obj).split('_')[0])
    
    #check if the month is janary -- if so, set to 12 if not, subtract one
    if month_int == 1:
        mont = 12
        new_month_id = str(year_int-1)+'_'+str(mont)
    else:
        mont = int(month_int-1)
        new_month_id = str(year_int)+'_'+str(mont)
        
    return new_month_id    


# # Pull in the other simpler data sets (demogs, arson, topo, infr)

# In[12]:


#topography
#no need to shift -- no month ids
topo_df = pd.read_csv(os.path.join(data_dir, 'clean_data/topography/grid_elevation.csv'))
topo_df['GRID_ID'] = topo_df['GRID_ID'].astype(int)
topo_df = topo_df.drop(columns=topo_df.columns[0])


# In[13]:


#infrastructure
#shift month up 1
infr_df = pd.read_csv((os.path.join(data_dir, 'clean_data/grid_infrastructure/grid_infrastructure_monthly.csv')))
infr_df['GRID_ID'] = infr_df['GRID_ID'].astype(int)
infr_df['month_id_old'] = infr_df['month_id']
infr_df['month_id'] = infr_df['month_id'].apply(lambda x: add_one_month(x))
infr_df = infr_df.drop(columns=infr_df.columns[0])


# In[14]:


#demographics
#shift up a year
demographics_df = pd.read_csv((os.path.join(data_dir, 'clean_data/ca_demogs/demogs_arson_master.csv')))
demographics_df['YEAR'] = demographics_df['YEAR']+1


# In[15]:


#pull in built fire features
#no need to shift
fire_feat = pd.read_csv((os.path.join(data_dir, 'clean_data/engineered_features/adj_fire_final.csv')))
fire_feat['GRID_ID'] = fire_feat['GRID_ID'].astype(int)


# # Merge with these

# In[16]:


#merge with topo
target_data_month_df = target_data_month_df.merge(topo_df, on='GRID_ID', how='left')

#merge with infrastructure
target_data_month_df = target_data_month_df.merge(infr_df, on=['GRID_ID','month_id'], how='left')

#merge with demographics
target_data_month_df = target_data_month_df.merge(demographics_df, on=['GRID_ID', 'NAME', 'COUNTYFP', 'YEAR'], how='left')

#merge with other fire
target_data_month_df = target_data_month_df.merge(fire_feat, on=['GRID_ID','month_id'], how='left')


# # Pull in and merge with weather

# In[17]:


#weather 
era_weather = pd.read_pickle((os.path.join(data_dir, 'clean_data/ERA_weather-data/ERA5_CAgrid_gdf.pkl')))
era_weather['GRID_ID'] = era_weather['GRID_ID'].astype(int)


#add in a month_id column
#need to shift up a month
era_weather['month'] = pd.DatetimeIndex(era_weather['date']).month
era_weather['YEAR'] = pd.DatetimeIndex(era_weather['date']).year
era_weather['month_id'] = era_weather['YEAR'].astype(str)+'_'+era_weather['month'].astype(str)
era_weather['month_id_old'] = era_weather['month_id']
era_weather['month_id'] = era_weather['month_id'].apply(lambda x: add_one_month(x))
era_weather = era_weather.drop(columns=['date','month','YEAR'])


# In[18]:


#merge weather
target_data_month_df = target_data_month_df.merge(era_weather, on=['GRID_ID','month_id'], how='left')


# # Final Clean Up and Send to Pickle

# In[19]:


#still need to handle shifting
#issue appears to be on januarys
target_data_month_df.loc[target_data_month_df['Total precipitation hrs:12'].isna()].groupby(['GRID_ID','month_id'])['month_id'].count()
#target_data_month.loc[target_data_month['Total precipitation hrs:12'].isna()].loc[target_data_month['YEAR']==2017]
target_data_month_df.loc[target_data_month_df['Total precipitation hrs:12'].isna()].shape[0]


# In[20]:


#dropping jan 1990 with no weather data from the previous month
target_df_final = target_data_month_df.loc[target_data_month_df['month_id']!='1990_1']
target_df_final.describe()


# In[21]:


#re-read in county grid to join with geometry
county_grid = gpd.read_file(os.path.join(data_dir, 'clean_data/county_grid/county_grid.dbf'))
county_grid['GRID_ID'] = county_grid['GRID_ID'].astype(int)


# In[22]:


#merge this with the initial df to get geometry
target_df_final_geo = target_df_final.merge(county_grid[['GRID_ID','geometry']], on='GRID_ID', how='left')


# In[27]:


#final column clear up
target_df_final_geo['geometry'] = target_df_final_geo['geometry_x']
target_df_final_geo = target_df_final_geo.drop(columns=['geometry_x', 'geometry_y','month_id_old_x','month_id_old_y'])


# In[28]:


#send to pickle file and csv
target_df_final_geo.to_pickle(os.path.join(data_dir, 'clean_data/target_df_final_geo.pkl'))
#target_df_final_geo.to_csv(os.path.join(data_dir, 'clean_data/target_df_final_geo.csv'))


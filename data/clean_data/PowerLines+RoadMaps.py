#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


# In[42]:


#read in counties file
count_gpd = gpd.read_file('CA_Counties_TIGER2016.shp')
#create slimmed down gpd to use for joining
counties = count_gpd[['COUNTYFP', 'NAME','geometry']]
counties['geometry'].plot(figsize=(8,8))


# In[43]:


#read in power line file
pl = gpd.read_file('California_Electric_Transmission_Lines.shp')
#select columns to keep
powerlines = pl[['OBJECTID', 'Name', 'kV_Sort', 'Owner', 'Status', 'Last_Edi_1','geometry']]
#plot
powerlines['geometry'].plot(figsize=(8,8))


# In[53]:


#read in roads file
roads_gpd = gpd.read_file('tl_2019_06_prisecroads.shp')
#select column
roads = roads_gpd[['LINEARID', 'RTTYP','geometry']]
#plot
roads['geometry'].plot(figsize=(8,8))


# In[83]:


powerline_gdf = gpd.sjoin(powerlines, counties, op='intersects', how='left')
powerline_gdf.to_file("powerline_clean.shp")


# In[84]:


roads = roads.to_crs('epsg:3857')
roads_gdf = gpd.sjoin(roads, counties, op='intersects', how='left')
roads_gdf.to_file("roads_clean.shp")


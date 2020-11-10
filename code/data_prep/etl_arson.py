#!/usr/bin/env python
# coding: utf-8

# # California Arson Data

# Import and preprocess California demographic data.
# 
# Arson – any willful or malicious burning or attempt to burn, with or without intent to defraud, a dwelling house, public building, motor vehicle or aircraft, personal property of another, etc. (UCR definition).
# 
# Contains the following fields by county by year from 1985 to 2019:
#  * Arson: Number of Structural Properties
#  * Arson: Number of Mobile Properties
#  * Arson: Number of Other Properties
#  * Number of Arsons
#  * Number of Arsons Cleared
#  
# Columns: ['Year', 'County', 'NCICCode', 'TotalStructural_sum', 'TotalMobile_sum',
#        'TotalOther_sum', 'GrandTotal_sum', 'GrandTotClr_sum']

# In[35]:


import pandas as pd
import numpy as np


# In[62]:


#Import the data
gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
subdir_from = 'data\\raw_data\\arson_crimes\\'
filename_from = 'arson_typed.csv'

df = pd.read_csv(gitdir + subdir_from + filename_from)

subdir_map = 'data\\clean_data\\'
filename_map = 'FIPS_clean.txt'

df_map = pd.read_csv(gitdir + subdir_map + filename_map)


# In[63]:


#Clean the data
df['County Name'] = df['County'].astype(str).str[:-7] #Trim county name
df = df.rename(columns={"TotalStructural_sum": "Structure Arsons", "TotalMobile_sum": "Mobile Arsons"                   , "TotalOther_sum": "Other Arsons", "GrandTotal_sum": "Total Arsons", "GrandTotClr_sum": "Total Arsons Cleared"})

df = pd.merge(df, df_map, how='inner', on='County Name') #Join on county name to get the FIPS code

df = df.drop(['County', 'NCICCode', 'FIPS2'], axis=1) #Drop unnecessary columns

df = df.reindex(columns=['FIPS', 'County Name', 'Year', 'Structure Arsons', 'Mobile Arsons', 'Other Arsons', 'Total Arsons', 'Total Arsons Cleared']) #Reorder the columns for visibility


# In[66]:


#Save the cleaned dataframe
subdir_to = 'data\\clean_data\\arson_crimes\\'
filename_to = 'arson_clean.csv'
df.to_csv(gitdir + subdir_to + filename_to, index=False)


# ### Test the clean data

# In[65]:


#Import the data
#gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
#subdir = 'data\\clean_data\\arson_crimes\\'
#filename = 'arson_clean.csv'
#
#df = pd.read_csv(gitdir + subdir + filename)
#
#df.head()


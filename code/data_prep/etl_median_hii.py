#!/usr/bin/env python
# coding: utf-8

# # California Median HHI Data

# Import and preprocess California demographic data.
# 
# Contains the following fields by county for the year of 2018:
#  * Population
#  * Population by gender
#  * Population by age bucket
#  * Median age
#  * Median age by gender

# In[3]:


import pandas as pd
import numpy as np


# In[64]:


#Import the data
gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
subdir_from = 'data\\raw_data\\ca_demogs\\'
filename_from = 'median_hhi_typed.txt'

df = pd.read_csv(gitdir + subdir_from + filename_from, sep='\t')


# In[65]:


#Clean the data
df['FIPS'] = df['fips1'].astype(str).str[1:] #Format FIPS ID column
df['FIPS'] = df['FIPS'].astype(str).str.lstrip('0')
df['medianHHI2018'] = df['medianHHI2018'].str.replace(',', '') #Format HHI to float
df['medianHHI2018'] = df['medianHHI2018'].str.replace('$', '')
df['medianHHI2018'] = df['medianHHI2018'].astype(int)
df['County Name'] = df['name'].astype(str).str[0:-11] #Trim county name

df = df.drop(0, axis=0) #Summary row for all CA which we don't need
df = df.drop(['fips1', 'percentOfState', 'name'], axis=1) #Drop unnecessary columns

df = df.reindex(columns=['FIPS', 'County Name', 'medianHHI2018']) #Reorder the columns for visibility


# In[69]:


#Save the cleaned dataframe
subdir_to = 'data\\clean_data\\ca_demogs\\'
filename_to = 'median_hhi_clean.csv'
df.to_csv(gitdir + subdir_to + filename_to, index=False)


# ### Test the clean data

# In[68]:


#Import the data
#gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
#subdir = 'data\\clean_data\\ca_demogs\\'
#filename = 'median_hhi_clean.csv'
#
#df = pd.read_csv(gitdir + subdir + filename)
#
#df.head()


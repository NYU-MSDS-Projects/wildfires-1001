#!/usr/bin/env python
# coding: utf-8

# # California Unemployment Data

# Import and preprocess California unemployment data.
# 
# Contains the following fields by county by year from 2011 to 2019:
#  * Unemployment rate

# In[51]:


import pandas as pd
import numpy as np


# In[57]:


#Import the data
gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
subdir_from = 'data\\raw_data\\ca_demogs\\'
filename_from = 'unemployment_typed.txt'

df = pd.read_csv(gitdir + subdir_from + filename_from, sep='\t')


# In[58]:


#Clean the data
df['FIPS'] = df['fips1'].astype(str).str[1:] #Format FIPS ID column
df['FIPS'] = df['FIPS'].astype(str).str.lstrip('0')
df['Unemployment'] = df['unemploymentRatePercent']/100 #Format unemployment to percent
df['County Name'] = df['name'].astype(str).str[0:-11] #Trim county name

df = df.drop(0, axis=0) #Summary row for all CA which we don't need
df = df.drop(['fips1', 'unemploymentRatePercent', 'name'], axis=1) #Drop unnecessary columns

df = df.reindex(columns=['FIPS', 'County Name', 'year', 'Unemployment']) #Reorder the columns for visibility


# In[63]:


#Save the cleaned dataframe
subdir_to = 'data\\clean_data\\ca_demogs\\'
filename_to = 'unemployment_clean.csv'
df.to_csv(gitdir + subdir_to + filename_to, index=False)


# ### Test the clean data

# In[62]:


#Import the data
#gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
#subdir = 'data\\clean_data\\ca_demogs\\'
#filename = 'unemployment_clean.csv'
#
#df = pd.read_csv(gitdir + subdir + filename)
#
#df.head()


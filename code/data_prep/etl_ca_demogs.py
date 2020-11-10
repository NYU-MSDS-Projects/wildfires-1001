#!/usr/bin/env python
# coding: utf-8

# # California Demogs Data

# Import and preprocess California demographic data.
# 
# Contains the following fields by county by year:
#  * Population
#  * Population by gender
#  * Population by age bucket
#  * Median age
#  * Median age by gender
#  
# Column names: ['SUMLEV', 'STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'YEAR', 'POPESTIMATE',
#        'POPEST_MALE', 'POPEST_FEM', 'UNDER5_TOT', 'UNDER5_MALE', 'UNDER5_FEM',
#        'AGE513_TOT', 'AGE513_MALE', 'AGE513_FEM', 'AGE1417_TOT',
#        'AGE1417_MALE', 'AGE1417_FEM', 'AGE1824_TOT', 'AGE1824_MALE',
#        'AGE1824_FEM', 'AGE16PLUS_TOT', 'AGE16PLUS_MALE', 'AGE16PLUS_FEM',
#        'AGE18PLUS_TOT', 'AGE18PLUS_MALE', 'AGE18PLUS_FEM', 'AGE1544_TOT',
#        'AGE1544_MALE', 'AGE1544_FEM', 'AGE2544_TOT', 'AGE2544_MALE',
#        'AGE2544_FEM', 'AGE4564_TOT', 'AGE4564_MALE', 'AGE4564_FEM',
#        'AGE65PLUS_TOT', 'AGE65PLUS_MALE', 'AGE65PLUS_FEM', 'AGE04_TOT',
#        'AGE04_MALE', 'AGE04_FEM', 'AGE59_TOT', 'AGE59_MALE', 'AGE59_FEM',
#        'AGE1014_TOT', 'AGE1014_MALE', 'AGE1014_FEM', 'AGE1519_TOT',
#        'AGE1519_MALE', 'AGE1519_FEM', 'AGE2024_TOT', 'AGE2024_MALE',
#        'AGE2024_FEM', 'AGE2529_TOT', 'AGE2529_MALE', 'AGE2529_FEM',
#        'AGE3034_TOT', 'AGE3034_MALE', 'AGE3034_FEM', 'AGE3539_TOT',
#        'AGE3539_MALE', 'AGE3539_FEM', 'AGE4044_TOT', 'AGE4044_MALE',
#        'AGE4044_FEM', 'AGE4549_TOT', 'AGE4549_MALE', 'AGE4549_FEM',
#        'AGE5054_TOT', 'AGE5054_MALE', 'AGE5054_FEM', 'AGE5559_TOT',
#        'AGE5559_MALE', 'AGE5559_FEM', 'AGE6064_TOT', 'AGE6064_MALE',
#        'AGE6064_FEM', 'AGE6569_TOT', 'AGE6569_MALE', 'AGE6569_FEM',
#        'AGE7074_TOT', 'AGE7074_MALE', 'AGE7074_FEM', 'AGE7579_TOT',
#        'AGE7579_MALE', 'AGE7579_FEM', 'AGE8084_TOT', 'AGE8084_MALE',
#        'AGE8084_FEM', 'AGE85PLUS_TOT', 'AGE85PLUS_MALE', 'AGE85PLUS_FEM',
#        'MEDIAN_AGE_TOT', 'MEDIAN_AGE_MALE', 'MEDIAN_AGE_FEM']

# In[137]:


import pandas as pd
import numpy as np


# In[168]:


#Import the data
gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
subdir_from = 'data\\raw_data\\ca_demogs\\'
filename_from = 'ca_demogs.csv'

df = pd.read_csv(gitdir + subdir_from + filename_from)


# In[169]:


#Clean the data
df['FIPS'] = df['COUNTY'] #Format FIPS ID column
df['County Name'] = df['CTYNAME'].astype(str).str[:-7] #Trim county name

df['AGEUNDER13_TOT'] = df['UNDER5_TOT'] + df['AGE513_TOT']
df['AGE1424_TOT'] = df['AGE1417_TOT'] + df['AGE1824_TOT']
#df['AGE2544_TOT'] = df['AGE2544_TOT']
#df['AGE4564_TOT'] = df['AGE4564_TOT']
#df['AGE65PLUS_TOT'] = df['AGE65PLUS_TOT']

df = df.drop(['SUMLEV', 'STATE', 'STNAME', 'CTYNAME', 'COUNTY', 'UNDER5_TOT', 'UNDER5_MALE', 'UNDER5_FEM', 'AGE513_TOT'              , 'AGE513_MALE', 'AGE513_FEM', 'AGE1417_TOT', 'AGE1417_MALE', 'AGE1417_FEM', 'AGE1824_TOT', 'AGE1824_MALE'              , 'AGE1824_FEM', 'AGE16PLUS_TOT', 'AGE16PLUS_MALE', 'AGE16PLUS_FEM', 'AGE18PLUS_TOT', 'AGE18PLUS_MALE'              , 'AGE18PLUS_FEM', 'AGE1544_TOT', 'AGE1544_MALE', 'AGE1544_FEM', 'AGE2544_MALE', 'AGE2544_FEM', 'AGE4564_MALE'              , 'AGE4564_FEM', 'AGE65PLUS_MALE', 'AGE65PLUS_FEM', 'AGE04_TOT', 'AGE04_MALE', 'AGE04_FEM', 'AGE59_TOT'              , 'AGE59_MALE', 'AGE59_FEM', 'AGE1014_TOT', 'AGE1014_MALE', 'AGE1014_FEM', 'AGE1519_TOT', 'AGE1519_MALE'              , 'AGE1519_FEM', 'AGE2024_TOT', 'AGE2024_MALE', 'AGE2024_FEM', 'AGE2529_TOT', 'AGE2529_MALE', 'AGE2529_FEM'              , 'AGE3034_TOT', 'AGE3034_MALE', 'AGE3034_FEM', 'AGE3539_TOT', 'AGE3539_MALE', 'AGE3539_FEM', 'AGE4044_TOT'              , 'AGE4044_MALE', 'AGE4044_FEM', 'AGE4549_TOT', 'AGE4549_MALE', 'AGE4549_FEM', 'AGE5054_TOT', 'AGE5054_MALE'              , 'AGE5054_FEM', 'AGE5559_TOT', 'AGE5559_MALE', 'AGE5559_FEM', 'AGE6064_TOT', 'AGE6064_MALE', 'AGE6064_FEM'              , 'AGE6569_TOT', 'AGE6569_MALE', 'AGE6569_FEM', 'AGE7074_TOT', 'AGE7074_MALE', 'AGE7074_FEM', 'AGE7579_TOT'              , 'AGE7579_MALE', 'AGE7579_FEM', 'AGE8084_TOT', 'AGE8084_MALE', 'AGE8084_FEM', 'AGE85PLUS_TOT'              , 'AGE85PLUS_MALE', 'AGE85PLUS_FEM'], axis=1) #Drop unnecessary columns

df = df.reindex(columns=['FIPS', 'County Name', 'YEAR', 'POPESTIMATE', 'POPEST_MALE', 'POPEST_FEM', 'MEDIAN_AGE_TOT', 'MEDIAN_AGE_MALE'                         , 'MEDIAN_AGE_FEM', 'AGEUNDER13_TOT', 'AGE1424_TOT', 'AGE2544_TOT', 'AGE4564_TOT', 'AGE65PLUS_TOT'])


# In[172]:


#Save the cleaned dataframe
subdir_to = 'data\\clean_data\\ca_demogs\\'
filename_to = 'ca_demogs_clean.csv'
df.to_csv(gitdir + subdir_to + filename_to, index=False)


# ### Test the clean data

# In[173]:


#Import the data
#gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
#subdir = 'data\\clean_data\\ca_demogs\\'
#filename = 'ca_demogs_clean.csv'
#
#df = pd.read_csv(gitdir + subdir + filename)
#
#df.head()


#!/usr/bin/env python
# coding: utf-8

# # FIPS Mapping

# Create a mapping table for FIPS codes. Include a variety of forms to make joining easier.

# In[17]:


import pandas as pd
import numpy as np


# In[43]:


#Import the data
gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
subdir_from = 'data\\raw_data\\'
filename_from = 'FIPS.txt'

df = pd.read_csv(gitdir + subdir_from + filename_from, header=None, names=['County Full Name','FIPS2','State'])


# In[44]:


#Clean the FIPS mapping and add extra columns for joining purposes
df = df.drop('State', axis=1) #Drop the state column since we know these counties are all CA
df['County Name'] = df['County Full Name'].astype(str).str[:-7] #Trim the 'County' word in the names
df['FIPS2'] = df['FIPS2'].astype(str).str[1:6] #Trim the FIPS to just the numbers
df['FIPS'] = df['FIPS2'].astype(str).str[2:]
df['FIPS'] = df['FIPS'].astype(str).str.lstrip('0')

df = df.drop('County Full Name', axis=1)

df = df.reindex(columns=['FIPS', 'FIPS2', 'County Name']) #Reorder the columns for visibility


# In[46]:


#Save the cleaned dataframe
subdir_to = 'data\\clean_data\\'
filename_to = 'FIPS_clean.csv'
df.to_csv(gitdir + subdir_to + filename_to, index=False)


# ### Testing the clean data

# In[ ]:


#Import the data
#gitdir = 'C:\\Users\jades\\1001 Intro to Data Science Notebooks\\Project\\wildfires-1001\\'
#subdir = 'data\\clean_data\\'
#filename = 'FIPS_clean.csv'
#
#df = pd.read_csv(gitdir + subdir + filename)
#
#df.head()


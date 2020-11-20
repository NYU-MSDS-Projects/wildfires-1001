import pandas as pd  # provides interface for interacting with tabular data
import geopandas as gpd  # combines the capabilities of pandas and shapely for geospatial operations
from shapely.geometry import Point, Polygon, MultiPolygon  # for manipulating text data into geospatial shapes
from shapely import wkt  # stands for "well known text," allows for interchange across GIS programs
import rtree  # supports geospatial join
import os
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
import descartes
import sys
import itertools

##Start by creating empty array into which we will fill data for selected timeframe and area
def generate_target_frame(grid_data, min_year, max_year):
    '''
    Purpose:
    --------
    Create shell target dataframe that has dates and grid ids broken down at all time intervals we may be interested in
    (days, weeks, and months - creating all of these at once reduces need to merge and combine dataframes later)
    Inputs:
    ------
        - grid_data : GeoDataFrame that will tell us the number of sections of the map for each we want to create observations
        - min_year : minimum year for which we want to include training data (inclusive)
        - max_year : max year for which we want to include training data (inclusive)
    Output(s):
    ---------
        - target_frame: pandas DataFrame w/ two columns
            1. date : will have all dates on the user input time interval between min and max input dates
            2. GRID_ID : column of grid ids for each date (i.e. will be colmn with lots of repeated grid ids)
                                     
    '''
    #get number of map sections
    n_areas = len(grid_data)
    #get number of time intervals
    years = max_year - min_year + 1
    
    #Generate day data first
    target_frame = pd.DataFrame(pd.date_range(f'1/1/{min_year}', f'12/31/{max_year}', freq = 'D'), columns = ['date'])
    print(target_frame.shape)
    #Get year, month, and week values from this date column
    target_frame['year'] = target_frame['date'].apply(lambda x:x.year)
    target_frame['month'] = target_frame['date'].apply(lambda x:x.month)
    target_frame['week'] = target_frame['date'].apply(lambda x:x.week)
    
    #Generate month data
    target_frame['month_id'] = target_frame['year'].astype(str) + '_' + target_frame['month'].astype(str)
    
    #get min and max date values for each month and then merge back onto full dataframe
    month_grp = target_frame[['month_id', 'date']].groupby(['month_id']).agg({'date' : ['min', 'max']}).reset_index()
    month_grp.columns = ['_'.join(col).strip() for col in month_grp.columns.values]
    month_grp.rename(columns = {'month_id_': 'month_id', 'date_min': 'month_start', 'date_max': 'month_end'}, \
                     inplace = True)
    target_frame = target_frame.merge(month_grp, on = 'month_id')
    
    #Generate week data - deal with weeks that start in december (assign them to the previous year)
    target_frame['week_id'] = np.where((target_frame['month'] ==12) & (target_frame['week'] ==1),
                                        target_frame['year'].apply(lambda x: str(x+1))+"_"+ target_frame['week'].astype(str), 
                                       target_frame['year'].astype(str) + '_' + target_frame['week'].astype(str))
    
    #get min and max date values for each month and then merge back onto full dataframe
    print(target_frame[(target_frame['week']==1) & (target_frame['month']==12)])
    week_grp = target_frame[['week_id', 'date']].groupby(['week_id']).agg({'date' : ['min', 'max']}).reset_index()
    week_grp.columns = ['_'.join(col).strip() for col in week_grp.columns.values]
    week_grp.rename(columns = {'week_id_': 'week_id', 'date_min': 'week_start', 'date_max': 'week_end'}, \
                     inplace = True)
    week_grp.sort_values(['week_start'], inplace = True)
    target_frame = target_frame.merge(week_grp, on = 'week_id')
    
    n_dates = len(target_frame)
    #Duplicate dates x # of times for grid sections we have
    target_frame = pd.concat([target_frame]*n_areas)
    target_frame['GRID_ID'] = list(itertools.chain(*[np.repeat(i, n_dates) for i in grid_data['GRID_ID'].sort_values()]))
    target_frame.drop(['year', 'month', 'week'], inplace = True, axis = 1)
    return target_frame

def disaggregate_fire_data(grid, fire_data, min_year, max_year):
    ''' 
    Purpose: Create instances of wildfires occuring on a daily level. This function starts with daily because it
    is easier to aggregate up once we have all days represented in one dataframe
    -------
    Inputs:
    -------
        - grid : GeoDataFrame of grid sections
        - fire_data : GeoDataFrame of fire data
    '''
    fire_data = fire_data[(fire_data['YEAR']>=min_year) & (fire_data['YEAR']<=max_year)]
    #Overlay grid and fire to get intersection geometry (this will create a dataframe with a few more fire
    #instances than we had in the plain fire_data 
    ##** Note that this will automatically exclude grid sections where this is no fire
    fire_grid = gpd.overlay(grid, fire_data, how = 'intersection')
    fire_grid['FIRE_GRID_INT_AREA'] = fire_grid.geometry.area
    fire_grid.index = range((len(fire_grid)))
    
    #create list of fires that had to be dropped due to data isseus (i.e. start date after end date)
    fires_dropped = []
    disagg_fire = pd.DataFrame()
    for row in fire_grid.itertuples():
        date_range = pd.date_range(row[list(fire_grid.columns).index('start_date')+1], \
                                   row[list(fire_grid.columns).index('end_date')+1], freq = 'D')
        if len(date_range)> 365:
            fires_dropped.append(row[list(fire_grid.columns).index('FIRE_KEY')])
            continue
        if len(date_range) == 0:
            fires_dropped.append(row[list(fire_grid.columns).index('FIRE_KEY')])
            continue
        dup_fire_data = pd.concat([pd.Series(row[1:], index = list(fire_grid.columns)).to_frame().transpose()]*len(date_range))
        dup_fire_data['date'] = date_range
        disagg_fire = disagg_fire.append(dup_fire_data, ignore_index = True)
        if row[0] in(np.arange(0,9000, 250)):
            print(row[0], row[list(fire_grid.columns).index('GRID_ID')+1], len(disagg_fire))
            print(disagg_fire['date'].head())
    return disagg_fire, fires_dropped




#take in an object formatted as YYYY_MM and add a month
def add_one_month(month_id_obj):
    
    #turn this object into a string
    #split this and take the element after the '_'
    #turn this back into an int
    month_int = int(str(month_id_obj).split('_')[1])
    
    #check if the month is decemember -- if so, set to 1 if not, add one
    if month_int == 12:
        return 1
    else:
        return month_int+1
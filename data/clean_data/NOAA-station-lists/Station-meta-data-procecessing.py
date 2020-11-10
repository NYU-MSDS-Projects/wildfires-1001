import pandas as pd
import numpy as np
import os



##user-input:
home_dir = '/Users/pedrogalarza/Documents/NYU-MSDS/2020_fall/DSGA-1001/Project-Wildfire'


'''
Step 1
------
Load relevant dataframes:
    1. NOAA ghcnd Stations
    2. NOAA ghcnd inventory

Filter by california.
Reult: inventory and station info data frames for all of california
'''
data_dir = os.path.join(home_dir, 'wildfires-1001/data')

#NOAA ghcnd Stations
ghcnd_stations_path = gpd.read_file(os.path.join(data_dir, 'raw_data/NOAA-meta-data', 'ghcnd-station.txt'))

stations_infile = open(ghcnd_stations_path, 'r')
station_lines = stations_infile.readlines() 
stations_infile.close()

df_list = []
for line in station_lines:
    char_split_list = []
    char_split_list.append(line[:11])
    char_split_list.append(line[12:20])
    char_split_list.append(line[21:30])
    char_split_list.append(line[31:37])
    char_split_list.append(line[38:40])
    char_split_list.append(line[41:71])
    char_split_list.append(line[72:75])
    char_split_list.append(line[76:79])
    char_split_list.append(line[80:85])
    char_split_list = [x.strip() for x in char_split_list]
    df_list.append(char_split_list)

    
stations_df = pd.DataFrame(df_list, columns = ["ID","LATITUDE","LONGITUDE","ELEVATION","STATE","NAME","GSN FLAG","HCN/CRN FLAG","WMO ID"])
CA_stations_df= stations_df.where(stations_df["STATE"]=="CA").dropna() #filter CA station only


#NOAA ghcnd inventory
ghcnd_inventory_path = gpd.read_file(os.path.join(data_dir, 'raw_data/NOAA-meta-data', "ghcnd-inventory.txt"))
inventory_infile = open(ghcnd_inventory_path, 'r') 
inventory_lines = inventory_infile.readlines() 
inventory_infile.close()

df_list = []
for line in inventory_lines:
    char_split_list = []
    char_split_list.append(str(line[:11].strip()))
    char_split_list.append(float(line[12:20]))
    char_split_list.append(float(line[21:30]))
    char_split_list.append(str(line[31:35].strip()))
    char_split_list.append(int(line[36:40]))
    char_split_list.append(int(line[41:45]))
    #char_split_list = [x.strip() for x in char_split_list]
    df_list.append(char_split_list)
    
    
inventory_df = pd.DataFrame(df_list, columns = ["ID","LATITUDE","LONGITUDE","ELEMENT","FIRSTYEAR","LASTYEAR"]) #make inventory df
CA_inventory_df = inventory_df.where(inventory_df["ID"].isin(CA_stations_ID_list)).dropna() #filter CA stations only

'''
Step 2
------
Filter data frames by features and coverage of interest
'''

time_CAin_df = CAin_df.where((CA_inventory_df["LASTYEAR"] == 2020) & (CA_inventory_df["FIRSTYEAR"] <= 1990)).dropna() #filter inventory to include 1990-2020 only

combined_CA_element_list = time_CAin_df[["ID","ELEMENT"]].groupby('ID').agg(lambda x: x.tolist()) #flatten df so that entries in the "element" column are the list of elements collected at that station
combined_CA_element_list = combined_CA_element_list.reset_index() #reset index df should have 2 columns, col0: station ID, col1: elements list


element_list = ["TMAX","TMIN","PRCP"] #here we define an element list of interst, we'll use this to filter station by whether they contain all 3 elements.

##filters the flattened station DF to see if station contain ALL of the elements in "element_list"
subset_mask = np.zeros(len(combined_CA_element_list["ELEMENT"]))
for i,j in enumerate(combined_CA_element_list["ELEMENT"]):
     subset_mask[i] = set(element_list).issubset(set(j))

combined_CA_element_list["ELEMENT MASK"] = subset_mask
combined_CA_element_filter = combined_CA_element_list.where(combined_CA_element_list["ELEMENT MASK"] ==1).dropna()


working_station_list = CA_stations_df.where(CA_stations_df["ID"].isin(combined_CA_element_filter["ID"])).dropna() #return complete station information from the station for only sation that met our requirements


station_list_filename = #name sation list you wish to save
station_list_paths = os.path.join(data_dir, 'clean_data/NOAA-station-lists/')
working_station_list.to_csv(station_list_paths+ station_list_filename+".csv")
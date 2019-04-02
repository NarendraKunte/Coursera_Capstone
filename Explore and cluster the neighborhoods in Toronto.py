#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from bs4 import BeautifulSoup
import requests


# In[2]:


wikipage_can = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
wikipage_can_data = BeautifulSoup(wikipage_can,'lxml') # pull data out of wikipage using bs4
table_can_postalcode = wikipage_can_data.find('table') #find the portion with table with postal code and other details
column_values = table_can_postalcode.find_all('td') # capture all column values with <td> tag

element_count = len(column_values)

postcode = []
borough = []
neighborhood = []

for i in range(0, element_count, 3):
    postcode.append(column_values[i].text.strip())
    borough.append(column_values[i+1].text.strip())
    neighborhood.append(column_values[i+2].text.strip())


# In[3]:


df_can_postalcode = pd.DataFrame(data=[postcode, borough, neighborhood]).transpose()
df_can_postalcode.columns = ['Postcode', 'Borough', 'Neighborhood']


# In[4]:


#Remove elements with Not assigned neighborhood.
df_can_postalcode.drop(df_can_postalcode[df_can_postalcode['Borough'] == 'Not assigned'].index, inplace=True)
df_can_postalcode.loc[df_can_postalcode.Neighborhood == 'Not assigned', "Neighborhood"] = df_can_postalcode.Borough


# In[5]:


# Group the neighbourhood with same postal code
df_can = df_can_postalcode.groupby(['Postcode', 'Borough'])['Neighborhood'].apply(', '.join).reset_index()
df_can.columns = ['Postcode', 'Borough', 'Neighborhood']


# In[6]:


df_can.head()


# In[7]:


df_can.shape


# In[ ]:





# In[9]:


df_lat_long = pd.read_csv('https://cocl.us/Geospatial_data')
df_lat_long.columns = list(map(str, df_lat_long.columns))
df_lat_long.rename(columns={'Postal Code':'Postcode'}, inplace=True)
df_can_postcode_Lat_long=pd.merge(df_can, df_lat_long, on='Postcode', how='outer')
#df_can_postcode_Lat_long


# In[10]:


toronto_data = df_can_postcode_Lat_long[df_can_postcode_Lat_long['Borough'].str.contains('Toronto')].reset_index(drop=True)
#toronto_data


# In[11]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

#!conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# In[12]:


address = 'Toronto'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[13]:


# create map of New York using latitude and longitude values
map_can = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(toronto_data['Latitude'], toronto_data['Longitude'], toronto_data['Borough'], toronto_data['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_can)  
    
map_can


# In[14]:


#Defining Foursquare credential and 
CLIENT_ID = 'HUZKQA4G4BDMP11PECKG4SS00TZLK1AXU2U3T1JBAEUQTULE' # your Foursquare ID
CLIENT_SECRET = '0O44S52G3KF0JRJUQ2YFV51P15JKNZDQJQ0HAJ30OZQFM1N5' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[44]:


toronto_data.loc[6, 'Neighborhood']


# In[38]:


#Now, let's get the top 100 venues that are in "North Toronto West" within a radius of 500 meters.
neighborhood_latitude = toronto_data.loc[6, 'Latitude'] # neighborhood latitude value
neighborhood_longitude = toronto_data.loc[6, 'Longitude'] # neighborhood longitude value


# In[39]:


LIMIT = 100 # limit of number of venues returned by Foursquare API
radius = 500 # define radius
# create URL
url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    neighborhood_latitude, 
    neighborhood_longitude, 
    radius, 
    LIMIT)
url # display URL


# In[40]:


results = requests.get(url).json()
results


# In[41]:


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[42]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[43]:


print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))


# In[45]:


#Explore Neighborhoods in North Toronto West. 
def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[46]:


#Call function and display the venue list around North Toronto West. 
toronto_venue = getNearbyVenues(names=toronto_data['Neighborhood'],
                                   latitudes=toronto_data['Latitude'],
                                   longitudes=toronto_data['Longitude']
                                  )


# In[ ]:





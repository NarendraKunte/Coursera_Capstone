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


# In[6]:


#Remove elements with Not assigned neighborhood.
df_can_postalcode.drop(df_can_postalcode[df_can_postalcode['Borough'] == 'Not assigned'].index, inplace=True)
df_can_postalcode.loc[df_can_postalcode.Neighborhood == 'Not assigned', "Neighborhood"] = df_can_postalcode.Borough


# In[7]:


# Group the neighbourhood with same postal code
df_can = df_can_postalcode.groupby(['Postcode', 'Borough'])['Neighborhood'].apply(', '.join).reset_index()
df_can.columns = ['Postcode', 'Borough', 'Neighborhood']


# In[10]:


df_lat_long = pd.read_csv('https://cocl.us/Geospatial_data')
df_lat_long.columns = list(map(str, df_lat_long.columns))
df_lat_long.rename(columns={'Postal Code':'Postcode'}, inplace=True)
df_can_postcode_Lat_long=pd.merge(df_can, df_lat_long, on='Postcode', how='outer')
df_can_postcode_Lat_long


# In[ ]:





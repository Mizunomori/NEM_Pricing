from collections import namedtuple
import altair as alt
#from tkinter import Image
import math
import streamlit as st
import numpy as np
import time 
import pandas as pd
from geopy.geocoders import Nominatim 
import requests 
import json

st.title("NEM Pricing Calculator")
st.subheader("Inputs for Calculation") 

pv_size = st.text_input('Area of PV Array (ft^2)', '250')
pv_area = float(pv_size) * 0.09290304
st.write('The current array size is', pv_area, 'm^2') 

sys_cap = st.text_input('Capacity of Solar Array (kW)', '400')

state = zip_code = st.text_input('State of Residency', 'NY')
city= st.text_input('City of Residency', 'Ithaca')

zipcode = st.text_input('Zipcode', '14850')

place = state + ' ' + city + ' ' + zipcode
st.write('The location being queried is', place) 

geolocator = Nominatim(user_agent="geoapiExercises")

location = geolocator.geocode(place) 
coords = [str(location.latitude), str(location.longitude)]
st.write('Your Latitude and Longitude is: (' + coords[0]+ ', ' +coords[1] + ')') 

#Selecting Type of Module Used in Array
mod_options = ['Standard', 'Premium', 'Thin film'] 

module = st.selectbox('What type of modules are you using?', mod_options, index = 0)
st.write('You selected',module)
mod_df =pd.DataFrame({'Standard': [0], 'Premium': [1], 'Thin film': [2]})

module_type = mod_df[module][0]

#Tilt of the Soalr Cells relatie to horizontal
tilt = st.slider('Angle of Roof/Solar Array', min_value= 0, max_value = 45, value = round(float(coords[0])) ,step = 1)

#Selecting The Proper Array Arrangement
arr_options = ['Fixed - Open Rack', 'Fixed - Roof Mounted', '1-Axis', '1-Axis Backtracking', '2-Axis']
arr_df = pd.DataFrame({'Fixed - Open Rack':[0], 'Fixed - Roof Mounted':[1], '1-Axis':[2] \
,'1-Axis Backtracking':[3], '2-Axis':[4]})

array = st.selectbox('What type of array are you using?', arr_options, index = 1)
st.write('You selected',array)
array_type = arr_df[array][0]


#Azimuth angle
azi_options = ['S','SSW', 'SW','WSW','W','WNW', 'NW','NNW', 'N' ,'NNE','NE', 'ENE', 'E', 'ESE', 'SE','SSE']
azi_df = pd.DataFrame({'S':[0], 'SSW':[22.5], 'SW':[45],'WSW':[67.5],'W':[90],'WNW':[112.5], 'NW':[135],'NNW':[157.5],\
     'N':[180],'NNE':[202.5],'NE':[225], 'ENE':[247.5], 'E':[270], 'ESE':[297.5], 'SE':[315],'SSE':[337.5]}) 
azi = st.selectbox('What direction is your house/array facing approximately?', azi_options, index = 0)

azimuth = azi_df[azi][0]

# Now Add the losses your system will experience 
losses = st.slider('What percent of power do you expect your system to lose?', min_value = -5, max_value= 99, value = 15)


# Now Use the Latitude and Longitude Given to doan API pull of the soalr data from NREL 
api_pull = 'https://developer.nrel.gov/api/pvwatts/v6.json?lat=' + coords[0]+ '&lon='+ coords[1] + \
 + 'module_type=' + module_type, '&system_capacity=' + sys_cap + '&tilt=' + tilt + '&array_type=' + \
     array_type + '&azimuth=' + azimuth +'&losses=' + losses\
         + '&api_key=90IdyNRwQOO0iv3PXV6wPAbfHl8dKrBFXWDWBadf'



response_API = requests.get(api_pull) 
# ghi data is in kWh/m2/day
data =response_API.text
dict = json.loads(data) 
d2 = dict['outputs'] 

## Need to figure out how to access ghi data specifically by month 
df = pd.DataFrame.from_dict(d2, orient ='index')

st.dataframe(df)

# Calculate Power Generated 
cell_eff = st.slider('Solar Cell Efficiency', min_value= 10, max_value = 30, step = 1, value = 20) 

tilt = st.slider('Angle of Roof/Solar Array', min_value= 0, max_value = 45, value = round(float(coords[0])) ,step = 1)

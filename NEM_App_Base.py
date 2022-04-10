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

pv_size = st.text_input('Size of PV Array (kW)', '500')
st.write('The current array size is', pv_size, 'kW') 


state = zip_code = st.text_input('State of Residency', 'NY')
city= st.text_input('City of Residency', 'Ithaca')

zipcode = st.text_input('Zipcode', '14850')

place = state + ' ' + city + ' ' + zipcode
st.write('The location being queried is', place) 

geolocator = Nominatim(user_agent="geoapiExercises")

location = geolocator.geocode(place) 
coords = [str(location.latitude), str(location.longitude)]
st.write('Your Latitude and Longitude is: (' + coords[0]+ ', ' +coords[1] + ')') 

# Now Use the Latitude and Longitude Given to doan API pull of the soalr data from NREL 
api_pull = 'https://developer.nrel.gov/api/solar/solar_resource/v1.json?lat=' + coords[0]+ '&lon='+ coords[1] + '&api_key=90IdyNRwQOO0iv3PXV6wPAbfHl8dKrBFXWDWBadf'



response_API = requests.get(api_pull) 

data =response_API.text
dict = json.loads(data) 
d2 = dict['outputs'] 

## Need to figure out how to access ghi data specifically by month 
df = pd.DataFrame.from_dict(d2, orient ='index')

st.dataframe(df)

# Calculate Power Generated 
cell_eff = st.slider('Solar Cell Efficiency', min_value= 10, max_value = 30, step = 1) 

tilt = st.slider('Angle of Roof/Solar Array', min_value= 0, max_value = 45, value = int(coords[0]) ,step = 1)

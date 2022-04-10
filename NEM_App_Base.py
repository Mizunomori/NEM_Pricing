from collections import namedtuple
import altair as alt
#from tkinter import Image
import math
import streamlit as st
import numpy as np
import time 
import pandas as pd
from geopy.geocoders import Nominatim 


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

api_pull = 'https://developer.nrel.gov/api/solar/solar_resource/v1.xml?lat=' + coords[0]+ '&lon='+ coords[1] + '&api_key=90IdyNRwQOO0iv3PXV6wPAbfHl8dKrBFXWDWBadf' 


st.write('Your Latitude and Longitude is: (' + coords[0]+ ', ' +coords[1]) 

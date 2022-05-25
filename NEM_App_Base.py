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
from pvlib import location as loc
from pvlib import irradiance
import pandas as pd
from matplotlib import pyplot as plt
from plot_ghi_transposition import get_irradiance
from timezonefinder import TimezoneFinder 


st.title("NEM Pricing Calculator")


#pv_size = st.text_input('Area of PV Array (ft^2)', '250')
#pv_area = float(pv_size) * 0.09290304
#st.write('The current array size is', pv_area, 'm^2') 

st.header('Location')
st.subheader('From your location information we will be able to calculate the average amount of sunlight you would receive as well as the residential electricity prices.')


state = st.text_input('State of Residency', 'NY')
city= st.text_input('City of Residency', 'Ithaca')

zipcode = st.text_input('Zipcode', '14850')

place = state + ' ' + city + ' ' + zipcode
st.write('The location being queried is', place) 

geolocator = Nominatim(user_agent="geoapiExercises")

location = geolocator.geocode(place) 
coords = [str(location.latitude), str(location.longitude)]
lat = float(coords[0])
lon = float(coords[1])
st.write('Your Latitude and Longitude is: (' + coords[0]+ ', ' +coords[1] + ')') 

st.header('Solar Array')
st.subheader('The specifications of your solar system will determine its performance and how much you may potentially save.')
sys_cap = float(st.text_input('Capacity of Solar Array (kW)', '10'))
c = np.array([206.14285714, 2426.14285714,  -38.32142857])

install_cost = c[2]*sys_cap**2 +  sys_cap* c[1] + c[0]

st.write('Estimated installation cost for Array Size %3.2f kW before tax credits is $ %5.2f' %tuple([sys_cap, install_cost]))

#Selecting Type of Module Used in Array
mod_options = ['Standard', 'Premium', 'Thin film'] 

module = st.selectbox('What type of modules are you using?', mod_options, index = 0)
st.write('You selected',module)
mod_df =pd.DataFrame({'Standard': [0], 'Premium': [1], 'Thin film': [2]})

module_type = mod_df[module][0]

#Tilt of the Soalr Cells relatie to horizontal
tilt = st.slider('Angle of Roof/Solar Array', min_value= 0, max_value = 45, value = 30 ,step = 1)

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

# Now Use the Latitude and Longitude Given to doan API pull of the utility rates from NREL 
price_pull = 'https://developer.nrel.gov/api/utility_rates/v3.json?lat=' + coords[0]+ '&lon='+ coords[1] +'&api_key=90IdyNRwQOO0iv3PXV6wPAbfHl8dKrBFXWDWBadf'

response_API = requests.get(price_pull) 
# utility pricing data is in $/kWh 
Pdata =response_API.text
Pdict = json.loads(Pdata) 
Pd2 = Pdict['outputs'] 
price_df = pd.DataFrame.from_dict(Pd2) 
res_price = float(price_df.residential)

e_bill = float(st.text_input('What is your average electricity bill in the summer ($)?', '100'))
st.write('Price of electricity for a residential consumer in your area is $ %2.3f/kWh' %res_price)

# Calcualting monthly and daily energy usage
e_load = e_bill/res_price
e_daily = e_load/31

st.header('Results')

# Now Use the Latitude and Longitude Given to doan API pull of the solar data from NREL 
api_pull = 'https://developer.nrel.gov/api/pvwatts/v6.json?lat=' + coords[0]+ '&lon='+ coords[1]\
 + '&module_type=' + str(module_type) + '&system_capacity=' + str(sys_cap) + '&tilt=' + str(tilt) + '&array_type='\
    + str(array_type) + '&azimuth=' + str(azimuth) +'&losses=' + str(losses)\
         +'&api_key=90IdyNRwQOO0iv3PXV6wPAbfHl8dKrBFXWDWBadf'



response_API = requests.get(api_pull) 
# ghi data is in kWh/m2/day
data =response_API.text
dict = json.loads(data) 
d2 = dict['outputs'] 

## Need to figure out how to access ghi data specifically by month 
solar_df = pd.DataFrame.from_dict(d2)

#st.dataframe(solar_df)





NEM = 'NEM 2.0'

cost = np.zeros(13)
solar_prod = np.zeros(13) 
savings = np.zeros(13)

     
solar_prod[:12] = solar_df.ac_monthly
solar_prod[12] = np.sum(solar_prod[:12])
demand = e_load
for i in range(0,12): 
          
     if e_load >= solar_prod[i]:
          Ppi = res_price
          savings[i] = Ppi * solar_prod[i]
          cost[i] = Ppi * demand - savings[i]
           
     else: 
          Ppi = res_price -0.03
          savings[i] = Ppi * solar_prod[i]
          cost[i] = Ppi * demand - savings[i]



cost[12] = np.sum(cost[:12])
savings[12] = np.sum(savings)
Months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Tot']
fd = pd.DataFrame({'Month': Months, 'Solar Production (kWh)': solar_prod, 'Bill After Solar NEM ($)': cost, 'Savings ($)': savings})


st.dataframe(fd)


payback = install_cost/savings[12]

fig,axs = plt.subplots(1,1, figsize =(8,6))

axs.plot(Months[:12], cost[:12], '-')
axs.set_xlabel('Month')
axs.set_ylabel('Bill ($)')
axs.set_title('Bill vs. Month')
plt.rcParams['font.size'] = 13
st.pyplot(fig)

#If Smart Home we can caculate power over smaller timescales 

obj = TimezoneFinder()
tz = obj.timezone_at(lng = lon, lat = lat) 
site_location = loc.Location(lat, lon, tz=tz)

dates= ['07-01-2019', '07-01-2021','10-01-2019', '10-01-2021']
days = 31

dy_irad = np.zeros([4,744,2])
for i in range(0,len(dates)):
     dy_irad[i,:,:] = get_irradiance(site_location, dates[i], tilt, azimuth)
 
   

summ_irad = (dy_irad[0,:,:] + dy_irad[1,:,:])/2 
fall_irad = (dy_irad[2,:,:] + dy_irad[3,:,:])/2 


summ_hrs = np.zeros([24])
fall_hrs = np.zeros([24])
for j in range(0, 31):
     summ_hrs[:] = summ_hrs[:]+ summ_irad[j*24:(j*24+24),1]/31
     fall_hrs[:] = fall_hrs[:] + fall_irad[j*24:(j*24+24),1]/31 

summ_pwr = summ_hrs *.2
fall_pwr = fall_hrs * .2

summ = np.array([0.030123129, 0.028412052, 0.027893306, 0.0282233, 0.029348275, 0.028643837 \
     ,0.034073772, 0.038129946, 0.040214751, 0.040616718, 0.043581589, 0.046959892, 0.046221516, 0.047289287 \
          ,0.049114413, 0.051597397, 0.05465336, 0.054475666, 0.051541176, 0.054747908, 0.053664921, 0.04792486, 0.039092799, 0.033456129]) * e_daily

fall = np.array([0.027909024,	0.028068565,	0.028688672,	0.034958594,	0.036082744,	0.036810749,	0.048275996,	0.045167662,	0.042198906,\
     	0.042714116,	0.042488399,	0.044230298,	0.042157561,	0.04218743,	0.040286818,	0.041876612,	0.046910151,	0.057671775,	0.055978038,\
               	0.056256477,	0.051948516,	0.043169701,	0.03390215,	0.030061045]) *e_daily * .9

pm = res_price - 0.03 
pp = res_price

q_s = np.zeros([24])
q_f = np.zeros([24])
for h in range(0,23): 
     a_s = summ[h] + res_price
     a_f = fall[h] + res_price 
     qp_s = np.max([summ_pwr[h] +.01, a_s])
     qm_s = summ_pwr[h] - .05 
     qp_f = np.max([fall_pwr[h] +.01, a_f])
     qm_f = fall_pwr[h] - .05
     #calculations for summer  
     if summ_pwr[h]   != 0:
          while a_s*(qp_s+.05) - .5 * (qp_s+.05)**2 -pp*(qp_s+.05 - summ_pwr[h]) > a_s*(qp_s) - .5 * (qp_s)**2 -pp*(qp_s - summ_pwr[h]):
               qp_s = qp_s +.05
          while a_s*(qm_s-.05) - .5 * (qm_s-.05)**2 -pm*(qm_s+.05 - summ_pwr[h]) > a_s*(qm_s) - .5 * (qm_s)**2 -pm*(qm_s - summ_pwr[h]):
               qm_s = qm_s -.05
     else:
          while a_s*(qp_s+.05) - .5 * (qp_s+.05)**2 -pp*(qp_s+.05 - summ_pwr[h]) > a_s*(qp_s) - .5 * (qp_s)**2 -pp*(qp_s - summ_pwr[h]):
               qp_s = qp_s +.05
     Sps = a_s*(qp_s) - .5 * (qp_s)**2 -pp*(qp_s - summ_pwr[h])
     Sms = a_s*(qm_s) - .5 * (qm_s)**2 -pm*(qm_s - summ_pwr[h])
     Ses = a_s * summ_pwr[h] - .5*(summ_pwr[h]**2) 
     Ss = np.max([Sps,Sms,Ses])
     if Ss == Sps : 
          q_s[h] = qp_s 
     elif Ss == Sms: 
          q_s[h] = qm_s 
     else: 
          q_s[h] = summ_pwr[h] 

     #Calculations for fall
     if fall_pwr[h]   != 0:
          while a_s*(qp_f+.05) - .5 * (qp_f+.05)**2 -pp*(qp_f+.05 - fall_pwr[h]) > a_s*(qp_f) - .5 * (qp_f)**2 -pp*(qp_f - fall_pwr[h]):
               qp_f = qp_f +.05
          while a_s*(qm_f-.05) - .5 * (qm_f-.05)**2 -pm*(qm_f+.05 - fall_pwr[h]) > a_s*(qm_f) - .5 * (qm_f)**2 -pm*(qm_f - fall_pwr[h]):
               qm_f = qm_f -.05
     else:
          while a_s*(qp_f+.05) - .5 * (qp_f+.05)**2 -pp*(qp_f+.05 - fall_pwr[h]) > a_s*(qp_f) - .5 * (qp_f)**2 -pp*(qp_f - fall_pwr[h]):
               qp_f = qp_f +.05 
     
     Spf = a_f*(qp_f) - .5 * (qp_f)**2 -pp*(qp_f - fall_pwr[h])
     Smf = a_f*(qm_f) - .5 * (qm_f)**2 -pm*(qm_f - fall_pwr[h])
     Sef = a_f * fall_pwr[h] - .5*(fall_pwr[h]**2) 
     Sf = np.max([Spf,Smf,Sef])
     if Sf == Spf : 
          q_f[h] = qp_f 
     elif Sf == Smf: 
          q_f[h] = qm_f 
     else: 
          q_f[h] = fall_pwr[h] 

fig,axs = plt.subplots(1,1, figsize =(10,8))

hours = ['0',	'1',	'2',	'3',	'4',	'5',	'6',	'7',	'8',	'9', \
     	'10',	'11',	'13',	'14',	'15',	'16',	'17',	'18',	'19',	'20',	'21',	'22',	'23',	'24']

st.header('Impacts of NEM on Hourly Consumption')
st.write('Here we compare coonsumption behaviors before and after installation of solar. This behavior is determined by what is called a Surplus function, \
     something that express how much you value using electricity considering the amount that you are paying for it.')
axs.plot(hours, summ, '--', label = 'Summer Consumption Before')
axs.plot(hours, fall, '--', label = 'Fall Consumption Before') 
axs.plot(hours, q_s, '-', label = 'Summer Consumption w/ Solar') 
axs.plot(hours, q_f, '-', label = 'Fall Consumption w/ Solar')
axs.set_xlabel('Hour')
axs.set_ylabel('Demand (kWh)')
axs.set_title('Demand vs. Hour') 
axs.legend()
plt.rcParams['font.size'] = 11
st.pyplot(fig) 

hr_df = pd.DataFrame({'Hours': hours, 'Summer Before (kWh)' : summ, 'Summer w/ Solar (kWh)': q_s, 'Fall Before (kWh)': fall, 'Fall w/ Solar (kWh)': q_f})

st.dataframe(hr_df)

st.write('Somewhat counterintuitively, consumption tends to go up with the addition of solar. Think of it in the same context of excusing \
     eating a cooke because you have worked out. Since you are paying less, the Surplus function suggests that you can consume more.')
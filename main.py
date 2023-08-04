
from re import L
from typing import Tuple
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
from streamlit.connections import ExperimentalBaseConnection
import requests
import folium
from streamlit_folium import st_folium, folium_static

class sgWeatherConnection(ExperimentalBaseConnection["sgWeatherConnection"]):
    def _connect(self, **kwargs) -> "sgWeatherConnection":
        return self
    
    def query(param,r_date) -> Tuple[datetime,datetime,pd.DataFrame]:
        resp = requests.get(url="https://api.data.gov.sg/v1/environment/2-hour-weather-forecast?date_time="+r_date.strftime("%Y-%m-%dT%H:%M:%S"))
        data = resp.json()
        returnFrame = pd.DataFrame.from_dict(data["items"][0]["forecasts"])
        returnFrame.set_index('area')
        posDF = pd.DataFrame.from_dict(data["area_metadata"])
        posDF.set_index('name')
        returnFrame = pd.concat([returnFrame,posDF],axis=1)
        startDate = datetime.strptime(data["items"][0]["valid_period"]["start"][:-6],"%Y-%m-%dT%H:%M:%S")
        endDate = datetime.strptime(data["items"][0]["valid_period"]["end"][:-6],"%Y-%m-%dT%H:%M:%S")
        return (startDate,endDate,returnFrame)



st.write("2-hour Weather Forecast in Singapore")

nowtime = datetime.now(tz=ZoneInfo("Asia/Singapore"))

d_time = nowtime

select_d = st.date_input("Pick your date and time", key='date', value=d_time, max_value=nowtime, format="YYYY/MM/DD", disabled=False, label_visibility="visible")
select_t = st.time_input("Time here", key='time', value=d_time, disabled=False, label_visibility="hidden")

d_time = datetime.combine(select_d,select_t)

conn = st.experimental_connection('sgweather', type=sgWeatherConnection)
(startDate,endDate,weatherData) = conn.query(d_time)

st.write(startDate.strftime("%d/%m/%Y, %H:%M:%S")+" to "+endDate.strftime("%d/%m/%Y, %H:%M:%S"))
#st.dataframe(data=weatherData,use_container_width=True,hide_index=True)
m = folium.Map(location=[1.352083,103.819839],zoom_start = 11)
for index, row in weatherData.iterrows():
    if row['forecast'] == 'Partly Cloudy (Night)':
        set_icon = "fa-cloud-moon"
        set_color = "black"
    elif row['forecast'] == 'Partly Cloudy (Day)':
        set_icon = "fa-cloud-sun"
        set_color = "blue"
    elif row['forecast'] == 'Light Rain':
        set_icon = "fa-cloud-rain"
        set_color = "blue"
    elif row['forecast'] == 'Light Showers':
        set_icon = "fa-cloud-rain"
        set_color = "blue"
    elif row['forecast'] == 'Moderate Rain':
        set_icon = "fa-cloud-showers-heavy"
        set_color = "blue"
    elif row['forecast'] == 'Showers':
        set_icon = "fa-cloud-showers-heavy"
        set_color = "blue"
    elif row['forecast'] == 'Thundery Showers':
        set_icon = "fa-cloud-showers-water"
        set_color = "grey"
    elif row['forecast'] == 'Heavy Thundery Showers':
        set_icon = "fa-cloud-showers-water"
        set_color = "grey"
    elif row['forecast'] == 'Cloudy':
        set_icon = "fa-cloud"
        set_color = "blue"
    elif row['forecast'] == 'Fair & Warm':
        set_icon = "fa-sun"
        set_color = "orange"
    elif row['forecast'] == 'Fair Day':
        set_icon = "fa-sun"
        set_color = "orange"
    elif row['forecast'] == 'Fair (Night)':
        set_icon = "moon"
        set_color = "black"
    else:
        set_icon = "x-mark-to-slot"
        set_color = "red"

    folium.Marker([row['label_location']['latitude'], row['label_location']['longitude']],
                    popup="<strong>"+row['area']+"</strong><br/>"+row['forecast'],
                    icon=folium.Icon(color = set_color, icon=set_icon, prefix='fa')
                  ).add_to(m)
folium_static(m)

st.dataframe(data=weatherData[["area","forecast"]],use_container_width=True,hide_index=True)
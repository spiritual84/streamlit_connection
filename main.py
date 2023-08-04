
import string
from typing import Tuple, AnyStr
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import pandas as pd
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data
import json
import requests

class sgWeatherConnection(ExperimentalBaseConnection["sgWeatherConnection"]):
    def _connect(self, **kwargs) -> "sgWeatherConnection":
        return self
    
    def query(param,r_date) -> Tuple[datetime,datetime,pd.DataFrame]:
        resp = requests.get(url="https://api.data.gov.sg/v1/environment/2-hour-weather-forecast?date_time="+r_date.strftime("%Y-%m-%dT%H:%M:%S"))
        data = resp.json()
        returnFrame = pd.DataFrame.from_dict(data["items"][0]["forecasts"])
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
st.write(weatherData)

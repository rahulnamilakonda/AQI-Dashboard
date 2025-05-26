from datetime import time
from time import sleep
import streamlit as st
import plotly.express as px


from controller.aqi_controller import AQIController
from repo.aqi_repo import *
from utils.constants.enums import RealTimeAQI, Stats
from utils.helpers.helper import draw_near_by_stations, get_error_message, markdown

aqi_cont = AQIController()
aqi_repo = AQIRepo()


@st.cache_data
def get_real_time_aqi_w_cord(lat, long):
    try:
        res = aqi_repo.get_real_time_waqi(RealTimeAQI.LAT_LONG, lat=lat, long=long)
        return res
    except Exception as e:
        print(e)
        raise e


@st.cache_data
def get_real_time_aqi_near_by(lat: str, long: str, lat2: str, long2: str):
    try:
        res = aqi_repo.get_real_time_waqi(
            RealTimeAQI.LAT_LONG_RANGE, lat=lat, long=long, lat2=lat2, long2=long2
        )
        return res
    except Exception as e:
        raise e


def show_error(exception):
    message = get_error_message(exception)
    markdown(
        f"""
        <h2 style='text-align: center; color: red;'>{message}</h2>
        """
    )


markdown(
    """
<style>
            body{
            background-color: white;
            }

            .stApp{
            background-color: white,
            }
</style>
"""
)


markdown(
    """<h1 style='text-align: center; font-weight: bold;'>Air Quality Index (AQI)</h1>""",
)

st.image(r"C:\data-science-projects\waqi\assets\aqi_head.png", use_container_width=True)

exception = None
res = None
cordinates = None

try:
    cordinates = aqi_cont.get_current_gps_coordinates()
except Exception as e:
    exception = e

# cordinates = (11111, 22222)


if exception:
    show_error(exception)
elif not cordinates:
    show_error("Coordinates not found, Please check your network connection.")
else:
    markdown(
        f"<h2 style='text-align: center;'> Welcome, {aqi_cont.get_gretting()}</h2>"
    )
    markdown(
        f"<h3 style='text-align: center; font-weight: 300;'>You're Current Coordinates: <b>{cordinates[0]}, {cordinates[1]} </b> </h3>",
    )

    try:
        res = get_real_time_aqi_w_cord(cordinates[0], cordinates[1])
    except Exception as e:
        exception = e

    if exception:
        show_error(exception)

    if not res:
        show_error("Data not found")

    else:
        draw_raqi_forecast(aqi_cont, res)

        col1, col2, col3 = st.columns([1, 2, 1])
        aqi_lat, aqi_long = None, None
        near_cords = None
        button_click = None
        with col2:
            button_click = st.button(
                "Get nearby stations AQI", use_container_width=True
            )
            if button_click:
                aqi_lat, aqi_long = aqi_cont.cord_from_real_aqi_response(res)
                near_cords = aqi_cont.destination_point(
                    aqi_lat, aqi_long, distance_km=100, bearing_deg=120
                )

        if button_click:
            with st.spinner("Loading nearest AQI stations..."):

                try:
                    station_res = get_real_time_aqi_near_by(
                        aqi_lat,
                        aqi_long,
                        f"{near_cords[0]:.4f}",
                        f"{near_cords[1]:.4f}",
                    )
                except Exception as e:
                    exception = e

            if exception:
                show_error(exception)
            else:
                draw_near_by_stations(aqi_cont, station_res)

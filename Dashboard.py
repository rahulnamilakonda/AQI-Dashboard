from datetime import time
from time import sleep
import streamlit as st
import plotly.express as px
from streamlit_js_eval import get_geolocation


from controller.aqi_controller import AQIController
from repo.aqi_repo import *
from utils.constants.enums import RealTimeAQI, Stats
from utils.helpers.helper import (
    draw_footer,
    draw_header,
    draw_near_by_stations,
    draw_raqi_forecast,
    get_error_message,
    markdown,
)

st.set_page_config(page_title="Dashboard", layout="wide")

aqi_cont = AQIController()
aqi_repo = AQIRepo()

loc = get_geolocation()

# st.session_state.pop("res", None)
# st.session_state.pop("disable_input", None)


@st.cache_data
def get_real_time_aqi_w_cords(lat: str, lng: str):
    try:
        res = aqi_repo.get_real_time_waqi(RealTimeAQI.LAT_LONG, lat=lat, long=lng)
        return res
    except Exception as e:
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
    st.error(message)
    # markdown(
    #     f"""
    #     <h2 style='text-align: center; color: red;'>{message}</h2>
    #     """
    # )


draw_header()

exception = None
res = None
cordinates = None

if loc and "coords" in loc:
    st.success("📍 Your location was fetched successfully!")
    cordinates = (loc["coords"]["latitude"], loc["coords"]["longitude"])
else:
    exception = "Please enable location permission or result..."

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
        # cordinates[0], cordinates[1]
        res = get_real_time_aqi_w_cords(cordinates[0], cordinates[1])
    except Exception as e:
        exception = e

    if exception:
        show_error(exception)

    if not res:
        show_error("Data not found")

    else:
        draw_raqi_forecast(aqi_cont, res, show_cords=False)

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


markdown(
    """
    <div style='margin-top: 200px;'></div>
    """,
    unsafe_allow_html=True,
)
draw_footer()

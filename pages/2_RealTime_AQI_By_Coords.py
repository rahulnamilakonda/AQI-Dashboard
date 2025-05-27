import streamlit as st

from controller.aqi_controller import AQIController
from repo.aqi_repo import AQIRepo
from utils.constants.enums import RealTimeAQI
from utils.helpers.helper import (
    draw_footer,
    draw_header,
    draw_raqi_forecast,
    get_error_message,
    markdown,
)

st.set_page_config(page_title="Real Time AQI Cordinates", layout="wide")

draw_header(pname="By Cordinates")

aqi_cont = AQIController()
aqi_repo = AQIRepo()
res = st.session_state.get("res_cords", None)


@st.cache_data
def get_real_aqi_cords(lat: str, lng: str):
    try:
        res = aqi_repo.get_real_time_waqi(
            real_time_aqi=RealTimeAQI.LAT_LONG, lat=lat, long=lng
        )
        return res
    except Exception as e:
        raise e


def on_get_aqi_click():
    if lat and long and lat.strip() and long.strip():
        st.session_state["disable_input_cord"] = True
        st.session_state.pop("res_cords", None)
        st.session_state.pop("search_lat", None)
        st.session_state.pop("search_long", None)


def on_click_diff_cc():
    st.session_state.pop("res_cords", None)
    st.session_state.pop("search_lat", None)
    st.session_state.pop("search_long", None)
    st.session_state["disable_input_cord"] = False


if "disable_input_cord" not in st.session_state:
    st.session_state["disable_input_cord"] = False

# st.session_state["disable_input_cord"] = False
# st.session_state.pop("res", None)
# st.session_state.pop("disable_input", None)

col1, col2 = st.columns(2)
lat = st.session_state.get("search_lat", None)
long = st.session_state.get("search_long", None)

with col1:
    lat = st.text_input(
        label="Please Input Latitude:",
        disabled=st.session_state["disable_input_cord"],
        value=st.session_state.get("search_lat", None),
    )

with col2:
    long = st.text_input(
        label="Please Input Longitude: ",
        disabled=st.session_state["disable_input_cord"],
        value=st.session_state.get("search_long", None),
    )

get_aqi_button = st.button(
    label="Get AQI level",
    use_container_width=True,
    disabled=st.session_state["disable_input_cord"],
    on_click=on_get_aqi_click,
)

if get_aqi_button or "res_cords" in st.session_state:
    with st.spinner(text=f"Loading AQI"):

        if not lat or not long or not lat.strip() or not long.strip():
            st.info("Please provide Latitude and Longitude")

        else:
            try:
                if "res_cords" not in st.session_state:
                    res = get_real_aqi_cords(lat=lat, lng=long)
                    st.session_state["res_cords"] = res
                    st.session_state["search_lat"] = lat.strip()
                    st.session_state["search_long"] = long.strip()
                    st.success("Data loaded successfully.")

            except Exception as e:
                msg = get_error_message(e)
                st.error(f"{msg}")

            try_diff_contry = st.button(
                label="Try Different Cordinates",
                on_click=on_click_diff_cc,
                use_container_width=True,
            )

            if res:
                draw_raqi_forecast(
                    aqi_cont=aqi_cont,
                    res=res,
                    search_str=f"{st.session_state['search_lat']}, {st.session_state['search_long']}",
                )


markdown(
    """
    <div style='margin-top: 100px;'></div>
    """,
    unsafe_allow_html=True,
)
draw_footer()

import streamlit as st

from controller.aqi_controller import AQIController
from repo.aqi_repo import AQIRepo
from utils.constants.enums import RealTimeAQI
from utils.helpers.helper import (
    draw_footer,
    draw_header,
    draw_near_by_stations,
    draw_raqi_forecast,
    get_error_message,
    markdown,
)

st.set_page_config(page_title="Real Time AQI Near By Stations", layout="wide")

draw_header(pname="By Nearby Stations")

aqi_cont = AQIController()
aqi_repo = AQIRepo()
res = st.session_state.get("res_cords_range", None)


@st.cache_data
def get_real_aqi_cords(lat1: str, long1: str, lat2: str, long2: str):
    try:
        res = aqi_repo.get_real_time_waqi(
            real_time_aqi=RealTimeAQI.LAT_LONG_RANGE,
            lat=lat1,
            long=long1,
            lat2=lat2,
            long2=long2,
        )
        return res
    except Exception as e:
        raise e


def on_get_aqi_click():
    if (
        lat1
        and lat2
        and long1
        and long2
        and lat1.strip()
        and long1.strip()
        and lat2.strip()
        and long2.strip()
    ):
        st.session_state["disable_input_cord_range"] = True
        st.session_state.pop("res_cords_range", None)
        st.session_state.pop("search_lat_1", None)
        st.session_state.pop("search_long_1", None)
        st.session_state.pop("search_lat_2", None)
        st.session_state.pop("search_long_2", None)


def on_click_diff_cc():
    st.session_state.pop("res_cords_range", None)
    st.session_state.pop("search_lat_1", None)
    st.session_state.pop("search_long_1", None)
    st.session_state.pop("search_lat_2", None)
    st.session_state.pop("search_long_2", None)
    st.session_state["disable_input_cord_range"] = False


if "disable_input_cord_range" not in st.session_state:
    st.session_state["disable_input_cord_range"] = False
# st.session_state.pop("res_cords_range", None)
# st.session_state["disable_input_cord_range"] = False

# st.session_state.pop("res", None)
# st.session_state.pop("disable_input", None)

col1, col2 = st.columns(2)

lat1 = st.session_state.get("search_lat_1", None)
long1 = st.session_state.get("search_long_1", None)

with col1:
    lat1 = st.text_input(
        label="Please Input Latitude 1:",
        disabled=st.session_state["disable_input_cord_range"],
        value=st.session_state.get("search_lat_1", None),
        key="lat1",
    )

with col2:
    long1 = st.text_input(
        label="Please Input Longitude 2: ",
        disabled=st.session_state["disable_input_cord_range"],
        value=st.session_state.get("search_long_1", None),
        key="long1",
    )

lat2 = st.session_state.get("search_lat_2", None)
long2 = st.session_state.get("search_long_2", None)


col3, col4 = st.columns(2)

with col3:
    lat2 = st.text_input(
        label="Please Input Latitude 2:",
        disabled=st.session_state["disable_input_cord_range"],
        value=st.session_state.get("search_lat_2", None),
        key="lat2",
    )

with col4:
    long2 = st.text_input(
        label="Please Input Longitude 2: ",
        disabled=st.session_state["disable_input_cord_range"],
        value=st.session_state.get("search_long_2", None),
        key="long2",
    )

get_aqi_button = st.button(
    label="Get AQI level",
    use_container_width=True,
    disabled=st.session_state["disable_input_cord_range"],
    on_click=on_get_aqi_click,
)

if get_aqi_button or "res_cords_range   " in st.session_state:
    with st.spinner(text=f"Loading AQI"):

        if (
            not lat1
            or not lat2
            or not long1
            or not long2
            or not lat1.strip()
            or not long1.strip()
            or not lat2.strip()
            or not long2.strip()
        ):
            st.info("Please provide Latitude and Longitude")

        else:
            try:
                if "res_cords_range" not in st.session_state:
                    res = get_real_aqi_cords(
                        lat1=lat1, long1=long1, lat2=lat2, long2=long2
                    )
                    st.session_state["res_cords_range"] = res
                    st.session_state["search_lat_1"] = lat1.strip()
                    st.session_state["search_long_1"] = long1.strip()
                    st.session_state["search_lat_2"] = lat2.strip()
                    st.session_state["search_long_2"] = long2.strip()
                    st.success("Data loaded successfully.")

            except Exception as e:
                msg = get_error_message(e)
                st.info(f"{msg}")
                st.session_state.pop("disable_input_cord_range", None)
                st.session_state.pop("res_cords_range", None)

            try_diff_contry = st.button(
                label="Try Different Cordinates",
                on_click=on_click_diff_cc,
                use_container_width=True,
            )

            if res:
                draw_near_by_stations(aqi_cont=aqi_cont, station_res=res)
                # draw_raqi_forecast(
                #     aqi_cont=aqi_cont,
                #     res=res,
                #     search_str=f"{st.session_state['search_lat_1']}, {st.session_state['search_long_1']}, {st.session_state['search_lat_2']}, {st.session_state['search_long_2']}",
                # )


markdown(
    """
    <div style='margin-top: 100px;'></div>
    """,
    unsafe_allow_html=True,
)
draw_footer()

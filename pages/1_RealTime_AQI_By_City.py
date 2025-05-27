from time import sleep
import streamlit as st

from controller.aqi_controller import AQIController
from repo.aqi_repo import AQIRepo
from utils.constants.enums import RealTimeAQI
import logging as log
from utils.helpers.helper import (
    draw_footer,
    draw_header,
    draw_raqi_forecast,
    get_error_message,
    markdown,
)


@st.cache_data
def get_real_aqi_city(input_text):
    try:
        res = aqi_repo.get_real_time_waqi(
            city=input_text, real_time_aqi=RealTimeAQI.CITY_BASED
        )
        return res
    except Exception as e:
        raise e


def on_get_aqi_click():
    if input_text and input_text.strip():
        st.session_state["disable_input"] = True
        st.session_state.pop("res", None)
        st.session_state.pop("search_str", None)


def on_click_diff_cc():
    st.session_state.pop("res", None)
    st.session_state.pop("search_str", None)
    st.session_state["disable_input"] = False


aqi_cont = AQIController()
aqi_repo = AQIRepo()
res = st.session_state.get("res", None)

st.set_page_config(page_title="Real Time AQI City", layout="wide")
draw_header(pname="By City")


if "disable_input" not in st.session_state:
    st.session_state["disable_input"] = False
elif not st.session_state.get("res") and st.session_state.get("disable_input", False):
    st.session_state["disable_input"] = False


# st.session_state["disable_input"] = False

input_text = st.text_input(
    label="Please input the country/ city name: ",
    placeholder="Hyderabad",
    disabled=st.session_state["disable_input"],
    value=st.session_state.get("search_str"),
    key="city_input",
    # label="cityname",
)


get_aqi_button = st.button(
    label="Get AQI",
    disabled=st.session_state["disable_input"],
    use_container_width=True,
    on_click=on_get_aqi_click,
)


if get_aqi_button or "res" in st.session_state:
    with st.spinner(text=f"Loading {input_text} AQI"):

        if not input_text or not input_text.strip():
            st.info("Please provide valid city/country name")
        else:
            try:
                if "res" not in st.session_state:
                    res = get_real_aqi_city(input_text=input_text)
                    st.session_state["res"] = res
                    st.session_state["search_str"] = input_text.strip()
                    st.success("Data loaded successfully.")

            except Exception as e:
                msg = get_error_message(e)
                st.error(f"{msg}")

            col1, col2, col3, col4, col5 = st.columns(5)

            with col3:
                try_diff_contry = st.button(
                    label="Try Different Country/ City", on_click=on_click_diff_cc
                )

            if res:
                draw_raqi_forecast(
                    aqi_cont=aqi_cont,
                    res=res,
                    search_str=str(st.session_state["search_str"]).title(),
                )
            else:
                st.session_state.pop("res", None)
                st.session_state.pop("search_str", None)


markdown(
    """
    <div style='margin-top: 100px;'></div>
    """,
    unsafe_allow_html=True,
)

draw_footer()

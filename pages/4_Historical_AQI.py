from datetime import datetime
import json
import streamlit as st

from app_data.exceptions.app_exceptions import HistWAIErrorException
from controller.aqi_controller import AQIController
from repo.aqi_repo import AQIRepo
from repo.local_repo import LocalRepo
from utils.constants.enums import Measurements
from utils.helpers.helper import draw_footer, draw_header, get_error_message, markdown
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Real Time AQI City", layout="wide")

draw_header(pname="By Historical Data")

aqi_cont = AQIController()
aqi_repo = AQIRepo()


@st.cache_data(show_spinner=False)
def get_country():
    try:
        countries = aqi_repo.get_countries()
        return countries
    except Exception as e:
        raise e


@st.cache_data(show_spinner=False)
def get_stations_and_pollutants(country_id: int):
    try:
        stations_res = aqi_repo.get_locations(country_id)
        return stations_res
    except Exception as e:
        raise e


@st.cache_data(show_spinner=False)
def load_aqi_data(
    sensor_id: int, poll_name: str, from_year: int, to_year: int
) -> pd.DataFrame:
    try:
        from_date = datetime(year=from_year, month=1, day=1)
        to_date = datetime(year=to_year, month=12, day=31)

        aqi_local_repo = LocalRepo()
        measure_df = None

        lcl_df = aqi_local_repo.get_measurement_histroy(
            from_year=from_year, to_year=to_year, sensor_id=sensor_id
        )

        lcl_df["period_datetimeFrom_utc"] = pd.to_datetime(
            lcl_df["period_datetimeFrom_utc"]
        )

        lcl_max_lcl_date = lcl_df["period_datetimeFrom_utc"].max()

        if lcl_df.shape[0] < 1 or lcl_max_lcl_date < to_date:

            if lcl_max_lcl_date < to_date:
                from_date = lcl_max_lcl_date

            measure_res = aqi_repo.get_measurements(
                sensor_id=sensor_id,
                date_from=from_date,
                date_to=to_date,
                measurement=Measurements.DAYS,
            )

            flat_json = aqi_cont.get_flattended_measurement(measure_res, key="results")

            measure_df = aqi_cont.get_measurement_df(flat_json)

            aqi_local_repo.put_sql(df=measure_df, table_name="AIR_QUALITY_DATA")

            if lcl_max_lcl_date < to_date:
                measure_df = pd.concat([lcl_df, measure_df])
                measure_df.drop_duplicates(inplace=True)
        else:
            measure_df = lcl_df

        t_df = aqi_cont.get_transformed_measurement(measure_df)

        t_df = aqi_cont.get_imshow_df(t_df)
        st.session_state["t_df"] = t_df.to_dict()
        return t_df

    except KeyError as ke:
        raise HistWAIErrorException(error=f"Data not found for {poll_name} pollutant.")
    except Exception as e:
        raise e


def on_click_fetch():
    st.session_state.pop("measure_res", None)


def on_change_country():
    st.session_state.pop("stations_res", None)


# @st.cache_data(show_spinner='False')
# def get_measurements(sensor_id: int):
#     aqi_repo.get_measurements(sensor_id)

# st.session_state.pop("res", None)
# st.session_state.pop("disable_input", None)
countries_res = st.session_state.get("country_res", None)
stations_res = st.session_state.get("stations_res", None)
t_df = st.session_state.get("t_df", None)

selected_country = st.session_state.get("selected_country", None)
selected_station = st.session_state.get("selected_station", None)
selected_poll = st.session_state.get("selected_poll", None)
from_year = st.session_state.get("from_year", None)
to_year = st.session_state.get("to_year", None)

if not countries_res:
    with st.spinner("Loading"):

        if not countries_res:
            countries_res = get_country()

if countries_res:
    countries = aqi_cont.get_countries(country_res=countries_res)

    selected_country = st.selectbox(
        label="Countries",
        options=list(countries.keys()),
        placeholder="India",
        on_change=on_change_country,
    )

    if selected_country:
        st.session_state["selected_country"] = selected_country
        st.session_state["country_res"] = countries_res

        if not stations_res:
            with st.spinner("Loading stations"):
                if not stations_res:
                    stations_res = get_stations_and_pollutants(
                        countries[selected_country]
                    )

        if stations_res:
            stations = aqi_cont.get_stations(stations_res)
            selected_station = st.selectbox(
                label="Select Location", options=list(stations.keys())
            )

            if selected_station:
                st.session_state["selected_station"] = selected_station
                st.session_state["stations_res"] = stations_res

                sensors_poll = aqi_cont.get_pollutants_from_histry(
                    station_id=stations[selected_station],
                    stations_res=stations_res,
                )

                selected_poll = st.selectbox(
                    label="Select Pollutant", options=list(sensors_poll.keys())
                )

                current_year = datetime.now().year

                from_year = st.selectbox(
                    label="From Date",
                    options=[year for year in range(2020, current_year + 1)],
                )
                to_year = st.selectbox(
                    label="To Date",
                    options=[year for year in range(from_year + 1, current_year + 1)],
                )

                st.session_state["selected_poll"] = selected_poll
                st.session_state["from_year"] = from_year
                st.session_state["to_year"] = to_year

                fetch_data_bt = st.button(
                    "Fetch Data", use_container_width=True, on_click=on_click_fetch
                )

                if fetch_data_bt or t_df:

                    with st.spinner("Loading AQI data"):
                        t_df = pd.DataFrame.from_dict(t_df)
                        error_msg = None

                        if "t_df" not in st.session_state:
                            try:
                                t_df = load_aqi_data(
                                    sensor_id=sensors_poll[selected_poll],
                                    poll_name=selected_poll,
                                    from_year=from_year,
                                    to_year=to_year,
                                )
                            except Exception as e:
                                error_msg = get_error_message(e)

                        if error_msg:
                            st.error(error_msg)
                        else:
                            st.dataframe(t_df)

                            tickvals = list(range(1, len(t_df.columns) + 1))
                            ticktext = list(str(col) for col in t_df.columns)

                            fig = px.imshow(
                                t_df,
                                labels=dict(
                                    x="Days",
                                    y="Month-Year",
                                    color=f"{selected_poll} (Avg)",
                                ),
                                height=800,
                                color_continuous_scale="viridis",
                            )
                            fig.update_layout(
                                title=f"{selected_poll} Summary Average Heatmap"
                            )
                            fig.update_xaxes(
                                tickmode="array",
                                tickvals=tickvals,
                                ticktext=ticktext,
                                dtick=1,
                                tickson="labels",
                            )
                            st.plotly_chart(fig, use_container_width=True)


markdown(
    """
    <div style='margin-top: 200px;'></div>
    """,
    unsafe_allow_html=True,
)
draw_footer()

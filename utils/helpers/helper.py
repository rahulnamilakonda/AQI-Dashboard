import streamlit as st
import plotly.express as px

from app_data.exceptions.app_exceptions import (
    ClientSideException,
    ConnectionException,
    FetchDataException,
    ServerSideException,
    TimeOutException,
    WAQIErrorException,
)
from controller.aqi_controller import AQIController
from utils.constants.enums import Stats


def markdown(markdown: str, unsafe_allow_html=True):
    st.markdown(markdown, unsafe_allow_html=unsafe_allow_html)


def get_error_message(exception):

    print("Exception: ", exception)

    if type(exception) is type(TimeOutException):
        return "Timed out"
    elif type(exception) is ConnectionException:
        return "Connection not found"
    elif type(exception) is ClientSideException:
        return "Client side exception"
    elif type(exception) is ServerSideException:
        return "Server Error"
    elif type(exception) is FetchDataException:
        return "Failed to fetch data"
    elif type(exception) is WAQIErrorException:
        return "Failed to fetch data"
    else:
        return exception


def draw_near_by_stations(aqi_cont, station_res):
    station_res = aqi_cont.get_flattended_measurement(station_res, "data")
    station_res_df = aqi_cont.clean_all_stations_res(station_res)

    if not station_res:
        markdown(
            "<h6 style='text-align:center font-weight:italic'> Data not found</h6>"
        )
    else:
        with st.expander(f"Show near by stations data"):
            st.dataframe(station_res_df, hide_index=True)

        fig = px.scatter(
            data_frame=station_res_df,
            color_continuous_scale="plasma",
            x="station_name",
            size="aqi",
            color="aqi",
            labels={
                "station_name": "Location",
                "index": "AQI",
                "color": "AQI Levels",
            },
            title="AQI Levels Across Monitoring Locations",
        )
        st.plotly_chart(fig, use_container_width=True)


def draw_raqi_forecast(aqi_cont: AQIController, res: dict):
    aqi_val = aqi_cont.get_real_time_aqi(res)
    dom_ploutant = aqi_cont.get_dominant_pol(res)

    markdown(
        f"<h4 style='text-align:center; font-weight: 300;'> Current AQI at you're location is: <b>{aqi_val}</b> </h4>"
    )
    markdown(f"<h3> Dominent Polutant: {dom_ploutant} </h3>")

    pollutants = aqi_cont.filter_pollutants(res)
    col1, col2 = st.columns(2)

    with col1:
        st.dataframe(
            pollutants.sort_values("values", ascending=False),
            hide_index=True,
        )

    with col2:
        colors = px.colors.sequential.Plasma[: pollutants.shape[0]]

        fig = px.pie(
            data_frame=pollutants,
            names="Pollutants",
            values="values",
            height=320,
            title="Pollutants Ocupancy",
            color_discrete_sequence=colors,
        )
        st.plotly_chart(fig, use_container_width=True)

    df = aqi_cont.get_all_pollutants(res)
    # st.line_chart(df, x="")

    no_of_days = aqi_cont.get_rt_aqi_frcst_days(df)
    markdown(f"<h2> Forecast for next {no_of_days} days.</h2>")

    avail_poll_data = aqi_cont.get_avail_unique_pollutants(res)
    if avail_poll_data:
        pol_sel = st.segmented_control(
            "Pollutants: ",
            avail_poll_data,
            selection_mode="single",
            default=avail_poll_data[0],
        )
        if pol_sel:
            poll_df = aqi_cont.get_pollutant_forecast(res, pol_sel)
            poll_df = poll_df.reset_index()

            with st.expander(f"Show {pol_sel} Data"):
                st.dataframe(poll_df, hide_index=True)

            stats_sel = st.segmented_control(
                "",
                options=[
                    Stats.AVERAGE.name.title(),
                    Stats.MINIMUM.name.title(),
                    Stats.MAXIMUM.name.title(),
                ],
                selection_mode="single",
                default=Stats.AVERAGE.name.title(),
            )

            y = None
            print(stats_sel == Stats.AVERAGE.name.title())
            if stats_sel == Stats.AVERAGE.name.title():
                y = Stats.AVERAGE.value
            elif stats_sel == Stats.MINIMUM.name.title():
                y = Stats.MINIMUM.value
            elif stats_sel == Stats.MAXIMUM.name.title():
                y = Stats.MAXIMUM.value

            if stats_sel and y:
                st.subheader(f"{stats_sel} AQI by Day for {str(pol_sel).title()}")
                fig = px.line(
                    data_frame=poll_df,
                    x="day",
                    y=y,
                    color_discrete_sequence=["red"],
                    labels={"day": "Day", y: f"{stats_sel}"},
                )
                st.plotly_chart(fig, use_container_width=True)

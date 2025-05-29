import os
import streamlit as st
import plotly.express as px

from data.exceptions.app_exceptions import (
    ClientSideException,
    ConnectionException,
    FetchDataException,
    HistWAIErrorException,
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
        return "Connection not found, Please check your network connection."
    elif type(exception) is ClientSideException:
        return "Client side exception"
    elif type(exception) is ServerSideException:
        return "Server Error"
    elif type(exception) is FetchDataException:
        return "Failed to fetch data"
    elif type(exception) is WAQIErrorException:
        return exception.error
    elif type(exception) is HistWAIErrorException:
        return exception.error
    else:
        return exception


def draw_near_by_stations(aqi_cont: AQIController, station_res):
    station_res = aqi_cont.get_flattended_measurement(station_res, "data")

    if not station_res:
        markdown(
            "<h6 style='text-align:center font-weight:italic'> Data not found</h6>"
        )
    else:
        station_res_df = aqi_cont.clean_all_stations_res(station_res)
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


def draw_raqi_forecast(
    aqi_cont: AQIController, res: dict, search_str: str = None, show_cords=False
):
    aqi_val = aqi_cont.get_real_time_aqi(res)
    dom_ploutant = aqi_cont.get_dominant_pol(res)
    location = search_str if search_str else "your location"

    markdown(
        f"<h3 style='text-align: center'; > Dominant Pollutant: {dom_ploutant} </h3>"
    )

    # if show_cords:
    markdown(
        f"<h4 style='text-align:center; font-weight: 300;'> Current AQI at {location} is: <b>{aqi_val}</b> </h4>"
    )

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


def draw_header(pname=None):
    page_name = ""

    if pname:
        page_name = f"- {pname}"

    markdown(
        f"""<h1 style='text-align: center; font-weight: bold;'>Air Quality Index (AQI){page_name}</h1>""",
    )

    img_path = os.path.join("assets", "aqi_head.png")

    st.image(f"{img_path}", use_container_width=True)


def draw_footer():

    st.markdown(
        """
        ## Why is AQI (Air Quality Index) Important?

        The **Air Quality Index (AQI)** is a critical indicator of how clean or polluted the air is, and what associated health effects might be of concern for you or your community.

        ### 🚨 Key Reasons Why AQI Matters:

        - **🫁 Public Health:** High AQI levels are linked to respiratory diseases, heart conditions, and other health issues — especially for vulnerable groups like children, the elderly, and those with pre-existing conditions.
        - **🏙️ Environmental Awareness:** AQI helps people understand pollution trends in their area and take action, like avoiding outdoor activity when air is unhealthy.
        - **📊 Policy & Action:** Governments and organizations use AQI data to implement clean air policies, regulate emissions, and monitor the effectiveness of interventions.
        - **🧭 Personal Decision-Making:** Knowing the AQI lets individuals make informed decisions — whether to wear a mask, use air purifiers, or plan outdoor activities.

        ### 📍 Local Relevance

        Tracking real-time AQI helps you stay aware of your **immediate surroundings**, empowering you to protect yourself and your loved ones.

        > “When you can’t see air pollution, AQI helps you feel its presence.”

        ## AQI table
        """
    )

    markdown(
        """

    <table class="table table-bordered center" style="width:95%">
        <caption style="text-align:center; font-size: 1.7em;color:black;padding-bottom:5px"><strong>AQI Basics for Ozone and Particle Pollution</strong></caption>
        <thead>
            <tr style="background: rgb(225, 235, 244); color: black;">
                <th scope="col" style="text-align:center;width:15%;vertical-align: text-top;padding:5px;font-size:19px">Daily AQI Color</th>
                <th scope="col" style="text-align:center;width:15%;vertical-align: text-top;padding:5px;font-size:19px">Levels of Concern</th>
                <th scope="col" style="text-align:center;width:15%;vertical-align: text-top;padding:5px;font-size:19px">Values of Index</th>
                <th scope="col" style="text-align:center;width:30%;vertical-align: text-top;padding:5px;font-size:19px">Description of Air Quality</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background: rgb(0, 228, 0); color: black;">
                <td><strong>Green</strong></td>
                <td id="good"><strong>Good</strong></td>
                <td><strong>0 to 50</strong></td>
                <td><strong>Air quality is satisfactory, and air pollution poses little or no risk.</strong></td>
            </tr>
            <tr style="background:yellow; color: black;">
                <td><strong>Yellow</strong></td>
                <td id="mod"><strong>Moderate</strong></td>
                <td><strong>51 to 100</strong></td>
                <td><strong>Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.</strong></td>
            </tr>
            <tr style="background: rgb(255, 126, 0); color: black;">
                <td><strong>Orange</strong></td>
                <td id="sens"><strong>Unhealthy for Sensitive Groups</strong></td>
                <td><strong>101 to 150</strong></td>
                <td><strong>Members of sensitive groups may experience health effects. The general public is less likely to be affected.</strong></td>
            </tr>
            <tr style="background:red; color: black;">
                <td><strong>Red</strong></td>
                <td id="unh"><strong>Unhealthy</strong></td>
                <td><strong>151 to 200</strong></td>
                <td><strong>Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.</strong></td>
            </tr>
            <tr style="background: rgb(143, 63, 151);color:white;">
                <td><strong>Purple</strong></td>
                <td id="vunh"><strong>Very Unhealthy</strong></td>
                <td><strong>201 to 300</strong></td>
                <td><strong>Health alert: The risk of health effects is increased for everyone.</strong></td>
            </tr>
            <tr style="background: rgb(126, 0, 35 );color:white;">
                <td><strong>Maroon</strong></td>
                <td id="haz"><strong>Hazardous</strong></td>
                <td><strong>301 and higher</strong></td>
                <td><strong>Health warning of emergency conditions: everyone is more likely to be affected.</strong></td>
            </tr>
        </tbody>
    </table>

    """
    )

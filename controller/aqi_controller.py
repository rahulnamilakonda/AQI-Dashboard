import json
import math
import geocoder
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from timezonefinder import TimezoneFinder


from utils.constants.enums import Stats


class AQIController:

    def __init__(self):
        pass

    def filter_pollutants(self, res: dict) -> pd.DataFrame:
        pollutants = ["pm25", "pm10", "co", "no2", "o3", "so2"]
        df = pd.DataFrame(res["data"]["iaqi"])
        mod_df = (
            df.unstack()
            .unstack()
            .reset_index()
            .rename(columns={"index": "Pollutants", "v": "values"})
        )

        # px.bar(data, x='Pollutants', y='values', width=500, height=500)

        return mod_df[mod_df["Pollutants"].isin(pollutants)]

    def get_dominant_pol(self, res: dict) -> str:
        return res["data"]["dominentpol"]

    def get_real_time_aqi(self, res: dict) -> int:
        return res["data"]["aqi"]

    def get_avail_unique_pollutants(self, res: dict) -> list:
        return list(dict(res["data"]["forecast"]["daily"]).keys())

    def get_pollutant_forecast(self, res: dict, pollnt: str) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(res["data"]["forecast"]["daily"][pollnt])
        df["day"] = pd.to_datetime(df["day"])
        df.set_index("day", inplace=True)

        # fg = px.line(data_frame=aq, height=500, width=800, title='Pollutant UVI')
        # fg.update_layout(title={'text':'Pollutant UVI', 'x':0.5, 'xanchor':'center'})

        return df

    def get_rt_aqi_frcst_days(self, df: pd.DataFrame):
        return df["day"].unique().shape[0]

    def get_all_pollutants(self, res):
        pollnts = self.get_avail_unique_pollutants(res)
        result_dfs = []
        for pollnt in pollnts:
            temp_df = self.get_pollutant_forecast(res, pollnt)
            temp_df["pollutant"] = pollnt
            result_dfs.append(temp_df)

        result_df = pd.concat(result_dfs).reset_index()
        result_df["day"] = pd.to_datetime(result_df["day"])
        return result_df

    def get_all_polluntant_stats(self, df, stats: Stats) -> pd.DataFrame:
        pass
        # fig = make_subplots(cols=3, rows=1, shared_yaxes=True)

        # pollutants = list(data_gr['pollutant'].unique())

        # for i in range(len(pollutants)):
        #     print(pollutants[i])
        #     fig.add_trace(go.Scatter(x=data_gr[data_gr['pollutant'] == pollutants[i]]['day'], y=data_gr['avg'],name=pollutants[i]), row = 1, col=i+1,)

        # fig.update_layout(height=600, width=800, title_text=", ".join(pollutants), xaxis=dict(tickmode='linear'),)
        # fig.show()

    def get_flattended_measurement(self, res, key):
        """
        Key can be either "results" or "data"

        """
        res_dicts = res[key]
        flattened_dict = {}
        for i in range(len(res_dicts)):
            if type(res_dicts[i]) is list:
                lst_dicts = res_dicts[i]
                for j in range(len(lst_dicts)):
                    for key, val in lst_dicts[j].items():
                        self.__parse__(key, flattened_dict, val)
            else:
                for key, val in res_dicts[i].items():
                    self.__parse__(key, flattened_dict, val)

        return flattened_dict

    def __parse__(self, key, flattened_dict, val):
        if type(val) is dict:
            for key2, val2 in val.items():
                if type(val2) is dict:
                    for key3, val3 in val2.items():
                        if f"{key}_{key2}_{key3}" not in flattened_dict:
                            flattened_dict[f"{key}_{key2}_{key3}"] = []
                        flattened_dict[f"{key}_{key2}_{key3}"].append(val3)
                else:
                    if f"{key}_{key2}" not in flattened_dict:
                        flattened_dict[f"{key}_{key2}"] = []

                    flattened_dict[f"{key}_{key2}"].append(val2)

        else:
            if key not in flattened_dict:
                flattened_dict[key] = []
            flattened_dict[key].append(val)

    def get_measurement_df(self, res, sensor_id=None):
        df = pd.DataFrame.from_dict(res)
        if sensor_id:
            df["sensor_id"] = sensor_id

        return df

    def get_transformed_measurement(self, df) -> pd.DataFrame:
        try:
            t_df: pd.DataFrame = df[
                [
                    "value",
                    "parameter_name",
                    "parameter_units",
                    "period_datetimeFrom_utc",
                    "period_datetimeTo_utc",
                    "summary_min",
                    "summary_max",
                    "summary_q02",
                    "summary_q25",
                    "summary_median",
                    "summary_q75",
                    "summary_q98",
                    "summary_avg",
                    "summary_sd",
                ]
            ]
        except Exception as e:
            raise e

        t_df["period_datetimeTo_utc"] = pd.to_datetime(t_df["period_datetimeTo_utc"])
        t_df["period_datetimeFrom_utc"] = pd.to_datetime(
            t_df["period_datetimeFrom_utc"]
        )

        t_df["mid_datetime"] = t_df["period_datetimeFrom_utc"] + (
            (t_df["period_datetimeTo_utc"] - t_df["period_datetimeFrom_utc"]) / 2
        )

        estimated_df = (t_df["summary_q75"] - t_df["summary_q25"]) / 1.35

        t_df["summary_sd"] = t_df["summary_sd"].fillna(estimated_df)

        t_df["year_month"] = t_df["mid_datetime"].dt.to_period("M").astype(str)
        t_df["day"] = t_df["mid_datetime"].dt.day

        return t_df

    def destination_point(
        self, lat: int, long: int, distance_km: int = 50, bearing_deg: int = 90
    ):
        R = 6371  # Earth radius in km
        bearing = math.radians(bearing_deg)
        lat = math.radians(lat)
        long = math.radians(long)

        lat2 = math.asin(
            math.sin(lat) * math.cos(distance_km / R)
            + math.cos(lat) * math.sin(distance_km / R) * math.cos(bearing)
        )

        lon2 = long + math.atan2(
            math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat),
            math.cos(distance_km / R) - math.sin(lat) * math.sin(lat2),
        )

        return math.degrees(lat2), math.degrees(lon2)

    def clean_all_stations_res(self, res) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(res)
        df["station_name"] = df["station_name"].str.split(",").str.get(0)
        df["station_time"] = pd.to_datetime(df["station_time"])
        df["aqi"] = df["aqi"].astype(np.int16)

        return df

    # fig = px.scatter(data_frame=clean_df, x='station_name', size='aqi',labels={'station_name':'Location', 'index':'AQI',}, title='Location Vs AQI')
    # fig.update_traces(marker_color='blue')
    # fig.show()

    @st.cache_data
    def get_current_gps_coordinates(
        _self,
    ):
        try:
            g = geocoder.ip("me")
            if g.latlng is not None:
                return g.latlng
            else:
                return None
        except Exception as e:
            raise e

    def get_greeting_from_location(self, loc):
        if loc and "coords" in loc:
            lat = loc["coords"]["latitude"]
            lon = loc["coords"]["longitude"]
            local_time = self.get_local_time_from_coords(lat, lon)
            if local_time:
                hour = local_time.hour
                if 4 <= hour < 12:
                    return "🌅 Good Morning"
                elif 12 <= hour < 16:
                    return "☀️ Good Afternoon"
                else:
                    return "🌇 Good Evening"
        return "👋 Hello"

    def get_local_time_from_coords(self, lat, lon):
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lat=lat, lng=lon)
        if tz_name:
            tz = pytz.timezone(tz_name)
            return datetime.now(tz)
        return None

    def cord_from_real_aqi_response(self, res: dict) -> tuple:
        return tuple(res["data"]["city"]["geo"])

    def get_countries(self, country_res: dict, key: str = "results") -> dict:
        falternd_dict = self.get_flattended_measurement(res=country_res, key=key)
        falternd_df = self.get_measurement_df(res=falternd_dict)
        falternd_df_cname_id = falternd_df[["name", "id"]]
        falternd_df_cname_id = falternd_df_cname_id.sort_values("name", ascending=True)

        return dict(
            zip(
                falternd_df_cname_id["name"],
                falternd_df_cname_id["id"],
            )
        )

    def get_stations(self, stations_res: dict, key: str = "results") -> dict:
        faltened_dict = self.get_flattended_measurement(res=stations_res, key=key)
        for key in [
            "datetimeFirst",
            "datetimeLast",
            "datetimeFirst_utc",
            "datetimeFirst_local",
            "datetimeLast_utc",
            "datetimeLast_local",
        ]:
            faltened_dict.pop(key, None)

        faltened_df = self.get_measurement_df(faltened_dict)
        name_id_df = faltened_df[["name", "id"]]

        return dict(zip(name_id_df["name"], name_id_df["id"]))

    def get_pollutants_from_histry(
        self,
        stations_res: dict,
        station_id: str,
        key: str = "results",
    ):
        faltened_dict = self.get_flattended_measurement(res=stations_res, key=key)
        for key in [
            "datetimeFirst",
            "datetimeLast",
            "datetimeFirst_utc",
            "datetimeFirst_local",
            "datetimeLast_utc",
            "datetimeLast_local",
        ]:
            faltened_dict.pop(key, None)

        faltened_df = self.get_measurement_df(faltened_dict)
        sensor_df = faltened_df[faltened_df["id"] == station_id]["sensors"]
        flat_json = self.get_flattended_measurement(
            res={"sensors": sensor_df.values.tolist()[0]}, key="sensors"
        )
        s_df = self.get_measurement_df(flat_json)
        return dict(zip(s_df["parameter_displayName"], s_df["id"]))

    def get_imshow_df(self, df: pd.DataFrame, stats: Stats) -> pd.DataFrame:

        if stats == Stats.MAXIMUM:
            tdf = df.pivot(
                index="year_month",
                columns="day",
                values="summary_max",
            )
        elif stats == Stats.MINIMUM:
            tdf = df.pivot(
                index="year_month",
                columns="day",
                values="summary_min",
            )
        else:
            tdf = df.pivot(
                index="year_month",
                columns="day",
                values="summary_avg",
            )

        tdf = tdf.fillna(method="ffill").fillna(tdf.mean(numeric_only=True))
        return tdf

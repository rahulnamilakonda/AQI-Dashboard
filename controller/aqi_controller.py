import pandas as pd
import numpy as np


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

    def get_unique_pollutants(self, res: dict) -> int:
        return list(dict(res["data"]["forecast"]["daily"]).keys())

    def get_pollutant_forecast(self, res: dict, pollnt: str) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(res["data"]["forecast"]["daily"][pollnt])
        df["day"] = pd.to_datetime(df["day"])
        df.set_index("day", inplace=True)

        # fg = px.line(data_frame=aq, height=500, width=800, title='Pollutant UVI')
        # fg.update_layout(title={'text':'Pollutant UVI', 'x':0.5, 'xanchor':'center'})

        return df

    def get_all_pollutants(self, res):
        pollnts = self.get_unique_pollutants(res)
        result_dfs = []
        for pollnt in pollnts:
            temp_df = self.get_pollutant_forecast(res, pollnt)
            temp_df["pollutant"] = pollnt
            result_dfs.append(temp_df)

        result_df = pd.concat(result_dfs).reset_index()
        result_df["day"] = pd.to_datetime(result_df["day"])
        return result_df

    def get_all_polluntant_avg(self, res):
        pass
        # fig = make_subplots(cols=3, rows=1, shared_yaxes=True)

        # pollutants = list(data_gr['pollutant'].unique())

        # for i in range(len(pollutants)):
        #     print(pollutants[i])
        #     fig.add_trace(go.Scatter(x=data_gr[data_gr['pollutant'] == pollutants[i]]['day'], y=data_gr['avg'],name=pollutants[i]), row = 1, col=i+1,)

        # fig.update_layout(height=600, width=800, title_text=", ".join(pollutants), xaxis=dict(tickmode='linear'),)
        # fig.show()

    def get_flattended_measurement(self, res):
        res_dicts = res["results"]
        flattened_dict = {}
        for i in range(len(res_dicts)):
            for key, val in res_dicts[i].items():
                if type(val) is dict:

                    for key2, val2 in val.items():
                        if type(val2) is dict:

                            for key3, val3 in val2.items():
                                if f"{key}_{key2}_{key3}" not in flattened_dict:
                                    flattened_dict[f"{key}_{key2}_{key3}"] = []
                                flattened_dict[f"{key}_{key2}_{key3}"].append(val3)

                        if f"{key}_{key2}" not in flattened_dict:
                            flattened_dict[f"{key}_{key2}"] = []

                        flattened_dict[f"{key}_{key2}"].append(val2)

                else:

                    if key not in flattened_dict:
                        flattened_dict[key] = []
                    flattened_dict[key].append(val)

        return flattened_dict

    def get_measurement_df(self, res):
        return pd.DataFrame.from_dict(res)

    def get_transformed_measurement(self, df) -> pd.DataFrame:
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

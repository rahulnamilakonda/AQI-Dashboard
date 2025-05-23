import requests
import json
import traceback
from app_data.exceptions.app_exceptions import WAQIErrorException
from app_data.network.network_services import NetworkServices
from models.open_qi_response_model import OpenQIResponse
from utils.constants.api_constants import WAQI_ERROR_STATUS, WAQI_SUCCESS_STATUS
from utils.constants.enums import RealTimeAQI, Measurements
from utils.constants.urls import (
    GET_COUNTRIES,
    GET_MEASUREMENTS_BY_SENSOR_ID_DAYS,
    WQAPI_REAL_TIME_CITY,
    GET_LOCATIONS,
)
from config.tokens import OPENAQ_TOKEN, WAQI_TOKEN
from main import DEBUG


class AQIRepo:

    def __init__(self):
        self.ntws = NetworkServices()
        self.headers = {"X-API-KEY": OPENAQ_TOKEN}
        self.WAQI_TOKEN = WAQI_TOKEN

    def get_real_time_waqi(
        self,
        real_time_aqi: RealTimeAQI,
        city: str = None,
        lat: str = None,
        long: str = None,
        lat2: str = None,
        long2: str = None,
    ) -> dict:

        # https://api.waqi.info/feed/india/?token=<TOKEN>
        r_url = None
        parms = {"token": self.WAQI_TOKEN}

        if real_time_aqi == RealTimeAQI.CITY_BASED:
            assert city != None, "Please provide city"
            r_url = f"{RealTimeAQI.CITY_BASED.value}".format_map({"city": city})

        elif real_time_aqi == RealTimeAQI.LAT_LONG:
            assert lat != None and long != None, "Please provide Lat and Long"
            r_url = f"{RealTimeAQI.LAT_LONG.value}".format_map(
                {"lat": lat, "long": long}
            )

        elif real_time_aqi == RealTimeAQI.LAT_LONG_RANGE:
            assert (
                lat != None and long != None and lat2 != None or long2 != None
            ), "Please provide Lat, Lat2 and Long, Long2"
            r_url = f"{RealTimeAQI.LAT_LONG_RANGE.value}"
            parms["latlng"] = f"{lat},{long},{lat2},{long2}"

        else:
            assert real_time_aqi in RealTimeAQI, "Please provide valid real time aqi"

        try:
            response = r_url
            response = self.ntws.get(r_url, parms=parms)

            if response["status"] == WAQI_SUCCESS_STATUS:

                if DEBUG:
                    with open("output.json", "w") as f:
                        json.dump(response, f)

                return response

            elif response["status"] == WAQI_ERROR_STATUS:
                if "data" in response:
                    raise WAQIErrorException(response["data"])

                elif "message" in response:
                    raise WAQIErrorException(response["message"])

        except Exception as e:
            raise e

    def get_countries(self) -> dict:
        parms = {"limit": 1000, "page": 1}
        pages_found = True
        response = OpenQIResponse()

        try:
            while pages_found:
                temp_response = self.ntws.get(
                    GET_COUNTRIES,
                    headers=self.headers,
                    parms=parms,
                )

                pages_found = self.__has_next_page__(
                    temp_response=temp_response, res=response
                )
                parms["page"] += parms["page"]

            return response.response

        except Exception as e:
            raise e

    # get country id's,parameters sensors ids.
    def get_locations(self, country_id: int) -> dict:
        parms = {"countries_id": country_id, "page": 1}
        pages_found = True
        response = OpenQIResponse()

        try:
            while pages_found:
                temp_response = self.ntws.get(GET_LOCATIONS, parms, self.headers)

                pages_found = self.__has_next_page__(
                    temp_response=temp_response, res=response
                )

                parms["page"] += parms["page"]

            return response.response

        except Exception as e:
            raise e

    def get_measurements(
        self, sensor_id: int, date_to: str, date_from: str, measurement: Measurements
    ):

        assert measurement in Measurements, "Please provide a valid measurement"

        parms = {
            "limit": 1000,
            # "sensors_id": sensor_id,
            date_from: date_from,
            date_to: date_to,
            "page": 1,
        }
        pages_found = True
        response = OpenQIResponse()
        r_url = measurement.value.format_map({"sensors_id": sensor_id})

        try:
            while pages_found:
                temp_response = self.ntws.get(r_url, parms, self.headers)

                pages_found = self.__has_next_page__(
                    temp_response=temp_response, res=response
                )
                parms["page"] += parms["page"]

            return response.response

        except Exception as e:
            raise e

    def __has_next_page__(self, temp_response, res: OpenQIResponse):

        if len(temp_response["results"]) < 1:

            if res.response is None:
                res.response = temp_response
            else:
                res.response["meta"] = temp_response["meta"]

            return False
        else:
            if res.response is None:
                res.response = temp_response
            else:
                res.response["meta"] = temp_response["meta"]
                res.response["results"].append(temp_response["results"])

            return True


if __name__ == "__main__":
    aqi = AQIRepo()
    try:
        aqi.get_real_time_waqi(city="Hyderabad")
    except Exception as e:
        print(e)

import requests
import json
import traceback
from app_data.exceptions.app_exceptions import WAQIErrorException
from app_data.network.network_services import NetworkServices
from utils.constants.api_constants import WAQI_ERROR_STATUS, WAQI_SUCCESS_STATUS
from utils.constants.urls import WQAPI_BASE_URL, GET_LOCATIONS
from config.tokens import WAQI_TOKEN
from main import DEBUG


class AQIRepo:

    def __init__(self):
        self.ntws = NetworkServices()

    def get_waqi_data(self, city: str) -> dict:

        # https://api.waqi.info/feed/india/?token=<TOKEN>
        r_url = f"{WQAPI_BASE_URL}/{city}/?token={WAQI_TOKEN}"

        try:
            response = r_url

            response = self.ntws.get(r_url)

            if response["status"] == WAQI_SUCCESS_STATUS:

                if DEBUG:
                    with open("output.json", "w") as f:
                        json.dump(response, f)

                return response

            elif response["status"] == WAQI_ERROR_STATUS and "data" in response:
                raise WAQIErrorException(response["data"])

            elif response["status"] == WAQI_ERROR_STATUS and "message" in response:
                raise WAQIErrorException(response["message"])

            # TODO:add message: invalidKey

        except Exception as e:
            raise e

    # get country id's,parameters sensors ids.
    def get_locations(self, country_id: int):
        parms = {"limit": "1000", "countries_id": country_id}
        try:
            response = self.ntws.get(GET_LOCATIONS)
        except:
            pass

    def get_measurements_by_day(self):
        pass

    def get_measurements_by_month(self):
        pass

    def get_measurements_by_year(self):
        pass


if __name__ == "__main__":
    aqi = AQIRepo
    try:
        aqi.get_waqi_data("Hyderabad")
    except Exception as e:
        print(e)

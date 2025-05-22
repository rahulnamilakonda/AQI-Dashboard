import requests
import json
import traceback
from app_data.network.network_services import NetworkServices
from utils.constants.urls import WQAPI_BASE_URL
from config.tokens import TOKEN
from main import DEBUG


def get_waqi_data(city: str) -> dict:
    nwts = NetworkServices()

    # https://api.waqi.info/feed/india/?token=<TOKEN>
    r_url = f"{WQAPI_BASE_URL}/{city}/?token={TOKEN}"

    try:
        response = nwts.get(r_url)

        if response["status"] == "ok":

            if DEBUG:
                with open("output.json", "w") as f:
                    json.dump(response, f)

            return response

        else:
            raise Exception(
                f"Exception while calling {WQAPI_BASE_URL}- " + str(response),
            )

    except Exception as e:
        raise e


if __name__ == "__main__":
    try:
        get_waqi_data("Hyderabad")

    except Exception as e:
        print(e)
        # traceback.print_exc()

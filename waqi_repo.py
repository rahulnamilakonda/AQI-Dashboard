import requests
import json
import traceback
from urls import WQAPI_BASE_URL
from tokens import TOKEN

TOKEN = ""
BASE_URL = f"https://api.waqi.info/feed"


def get_waqi_data(self, city: str) -> dict:

    # https://api.waqi.info/feed/india/?token=<TOKEN>
    r_url = f"{WQAPI_BASE_URL}/{city}/?token={TOKEN}"

    try:
        response = requests.get(r_url)

        if response.status_code == 200 and response.json()["status"] == "ok":
            return response.json()
            # with open("output.json", "w") as f:
            #     json.dump(response.json(), f)

        else:
            raise Exception(
                f"Exception while calling {WQAPI_BASE_URL}- " + str(response.json()),
            )

    except Exception as e:
        raise e


if __name__ == "__main__":
    try:
        get_waqi_data("")

    except Exception as e:
        print(e)
        # traceback.print_exc()

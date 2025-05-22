from app_data.network.base_api_services import BaseApiServices

import requests

from app_data.exceptions.app_exceptions import (
    ClientSideException,
    ConnectionException,
    FetchDataException,
    ServerSideException,
    TimeOutException,
)


class NetworkServices(BaseApiServices):

    def get(self, url):
        try:
            response = requests.get(url)
            return self.__get_response(response)
        except requests.exceptions.ReadTimeout as errrt:
            raise TimeOutException(errrt)
        except requests.exceptions.ConnectionError as erre:
            raise ConnectionException(erre)

    def __get_response(self, response: requests.Response):

        if response.status_code == 200:
            return response.json()

        elif response.status_code >= 400 and response.status_code <= 499:
            raise ClientSideException(str(response.json()))

        elif response.status_code >= 500 and response.status_code <= 599:
            raise ServerSideException(str(response.json()))

        else:
            raise FetchDataException(str(response.json()))

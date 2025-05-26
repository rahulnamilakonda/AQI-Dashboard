import streamlit as st

from app_data.exceptions.app_exceptions import (
    ClientSideException,
    ConnectionException,
    FetchDataException,
    ServerSideException,
    TimeOutException,
    WAQIErrorException,
)


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

"""Module with all functionality for scraping weather data."""

import base64

import functions_framework
import requests
from decouple import config


def get_data(city: str, tries: int):
    """Get weather data from 'Weather by API-Ninjas'."""
    if not tries:
        return
    response = requests.get(
        "https://weather-by-api-ninjas.p.rapidapi.com/v1/weather",
        headers={"X-RapidAPI-Key": config("X_RapidAPI_Key"), "X-RapidAPI-Host": config("X_RapidAPI_Host")},
        params={"city": city},
    )
    if response.status_code != 200:
        get_data(city, tries - 1)
    return response.text


@functions_framework.cloud_event
def get_weather_data(cloud_event):
    """Executed function(FaaS) for getting weather data."""
    get_data("Kyiv", 3)
    print(base64.b64decode(cloud_event.data["message"]["data"]))


print(get_data("Kyiv", 3))

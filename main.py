"""Module with all functionality for scraping weather data."""

import base64

import functions_framework


@functions_framework.cloud_event
def get_weather_data(cloud_event):
    """Executed function(FaaS) for getting weather data."""
    print(base64.b64decode(cloud_event.data["message"]["data"]))

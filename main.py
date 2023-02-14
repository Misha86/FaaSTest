"""Module with all functionality for scraping weather data."""

import base64
import datetime

import functions_framework
import pandas as pd
import requests
from decouple import config
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows


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
    return response.json()


def append_data_to_excel(file_path: str, df: pd.DataFrame):
    """Append data to the existing excel file."""
    wb = load_workbook(file_path, read_only=False)
    ws_sheet = wb["Sheet1"]
    for row in dataframe_to_rows(df, header=False, index=False):
        ws_sheet.append(row)
    wb.save(file_path)
    wb.close()


def save_data_to_excel(json_data: dict, city: str):
    """Save weather data to the excel file."""
    df = pd.DataFrame(
        [[datetime.datetime.now().strftime("%d.%m.%Y"), *json_data.values()]],
        columns=["date", *json_data.keys()],
    )
    file_path = f"weather_data_{city.lower()}1.xlsx"

    try:
        append_data_to_excel(file_path, df)
    except FileNotFoundError:
        df.to_excel(file_path, sheet_name="Sheet1", index=False)


@functions_framework.cloud_event
def get_weather_data(cloud_event):
    """Executed function(FaaS) for getting weather data."""
    city = "Kyiv"
    json_data = get_data(city, 3)
    if len(json_data) != 10:
        print(json_data)
    else:
        save_data_to_excel(json_data, city)
    print(base64.b64decode(cloud_event.data["message"]["data"]))

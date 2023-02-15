"""Module with all functionality for scraping weather data."""

import base64
import datetime
import os
import pickle

import functions_framework
import pandas as pd
import requests
from decouple import config
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class Credential:
    """Class to manage credentials."""

    def __init__(self) -> None:
        """Inits Credential."""
        self._creds = None
        self._token_file = "token_write.pickle"

    def _get_creds_pickle(self):
        """Get credentials data from the pickle file."""
        if os.path.exists(self._token_file):
            with open(self._token_file, "rb") as token:
                self._creds = pickle.load(token)

    def _save_creds_pickle(self):
        """Save credentials data to the pickle file."""
        with open(self._token_file, "wb") as token:
            pickle.dump(self._creds, token)

    def get_creds(self):
        """Get credentials data."""
        self._get_creds_pickle()
        if not self._creds or not self._creds.valid:
            if all([self._creds, self._creds.expired, self._creds.refresh_token]):
                self._creds.refresh(Request())
            self._save_creds_pickle()
        return self._creds


class SheetService:
    """Class to manage sheets services."""

    api_service_name = "sheets"
    api_version = "v4"

    def __init__(self, credentials: Credential) -> None:
        """Inits SheetService with args.

        Args:
            credentials (Credential): A Credential object, credentials to be used for
        authentication.
        """
        self._creds = credentials.get_creds()

    def create_service(self):
        """Create a new sheets service."""
        try:
            service = build(self.api_service_name, self.api_version, credentials=self._creds)
            print(self.api_service_name, "service created successfully")
            return service
        except Exception as err:
            print(err)
            return None


def export_data_to_sheets(service, sheet_id, sheet_range, df):
    """Push new data to the Google Spreadsheet."""
    sheet_settings = {"spreadsheetId": sheet_id, "range": sheet_range}
    sheet = service.spreadsheets().values()
    result_input = sheet.get(**sheet_settings).execute().get("values")
    export_settings = {
        "valueInputOption": "RAW",
        "body": dict(majorDimension="ROWS", values=df.T.reset_index(drop=bool(result_input)).T.values.tolist()),
        **sheet_settings,
    }

    if result_input:
        sheet.append(**export_settings).execute()
    else:
        sheet.update(**export_settings).execute()
    print("Sheet successfully Updated")


def get_api_data(city: str, tries: int = 3):
    """Get weather data from 'Weather by API-Ninjas'."""
    if not tries:
        return
    response = requests.get(
        config("WEATHER_API"),
        headers={"X-RapidAPI-Key": config("X_RapidAPI_Key"), "X-RapidAPI-Host": config("X_RapidAPI_Host")},
        params={"city": city},
    )
    if response.status_code != 200:
        get_api_data(city, tries - 1)
    return response.json()


def get_data_frame(json_data: dict):
    """Save weather data to the data frame."""
    return pd.DataFrame(
        [[datetime.datetime.now().strftime("%d.%m.%Y"), *json_data.values()]],
        columns=["date", *json_data.keys()],
    )


SAMPLE_SPREADSHEET_ID = config("SAMPLE_SPREADSHEET_ID")
SAMPLE_RANGE_NAME = "A1:AA1000"


@functions_framework.cloud_event
def get_weather_data(cloud_event):
    """Execute function(FaaS) for getting weather data and save to the Google Spreadsheet."""
    json_data = get_api_data("Kyiv")
    df = get_data_frame(json_data)
    credential = Credential()
    service = SheetService(credential).create_service()
    export_data_to_sheets(service, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, df)

    print(base64.b64decode(cloud_event.data["message"]["data"]))


if __name__ == "__main__":
    json_data = get_api_data("Kyiv")

    df = get_data_frame(json_data)

    credential = Credential()
    service = SheetService(credential).create_service()

    export_data_to_sheets(service, SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, df)

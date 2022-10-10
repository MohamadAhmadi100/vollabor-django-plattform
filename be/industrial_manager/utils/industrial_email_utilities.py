import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import datetime
import pathlib
from pprint import pprint

from ivc_project.settings import INDUSTRIAL_EMAIL_DATA_DIR


def get_data_from_google_sheet(username):
    """
    If file exists, we simply get the data from the server
    """
    file_exists = os.path.exists(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json')
    if file_exists:
        file = pathlib.Path(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json')
        last_modification_time = datetime.datetime.fromtimestamp(file.stat().st_mtime)
        with open(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json', 'r') as input_file:
            data = json.load(input_file)
            return True, len(data), last_modification_time

    """
    Otherwise we make a request too google sheet and get the data
    """
    return update_data(username)


def update_data(username):
    while True:
        try:
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                '../ivc_project/industrial_manager/utils/creds.json',
                scope)
            client = gspread.authorize(creds)
            sheet = client.open('companies').sheet1
            data = sheet.get_all_records()
            with open(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json', 'w') as file:
                json.dump(data, file)
            return True, len(data), datetime.datetime.now()
        except requests.exceptions.ConnectionError:
            pass


def get_country_list(username):
    file_exists = os.path.exists(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json')
    if file_exists:
        with open(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json', 'r') as input_file:
            data = json.load(input_file)
        country_set = set()
        for row in data:
            country = row['Country'].replace('\r', '').replace('\n', '')
            if country != '':
                country_set.add(country)
        return True, list(country_set)
    else:
        return False, []


def get_all_list(username):
    file_exists = os.path.exists(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json')
    if file_exists:
        with open(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json', 'r') as input_file:
            data = json.load(input_file)
        return True, len(data)
    else:
        return False, []


def get_country_numbers(username, country_name):
    file_exists = os.path.exists(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json')
    if file_exists:
        with open(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json', 'r') as input_file:
            data = json.load(input_file)

        numbers = 0
        for row in data:
            country = row['Country'].replace('\r', '').replace('\n', '')
            if country == country_name:
                numbers += 1
        return True, numbers
    else:
        return False, []


def get_last_modification_time(username):
    file_exists = os.path.exists(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json')
    if file_exists:
        file = pathlib.Path(f'{INDUSTRIAL_EMAIL_DATA_DIR}/mail_data_{username}.json')
        last_modification_time = datetime.datetime.fromtimestamp(file.stat().st_mtime)
        return True, last_modification_time
    else:
        return False, 0

"""
uses the api from https://www.aerisweather.com/
"""

import os
import requests
import json
import time

ID = ''
SECRET = ''
LOCATION = ''

DELAY = 30 * 60 # Updates every 30 minutes
CURRENTURL = 'https://api.aerisapi.com/conditions/{location}?format=json&plimit=1&fields=periods.tempF,periods.humidity,periods.windSpeedMPH,periods.windDir,periods.weather,periods.icon&client_id={id}&client_secret={secret}'
FORECASTURL = 'https://api.aerisapi.com/forecasts/{location}?format=json&filter=day&limit={days}&fields=periods.maxTempF,periods.minTempF,periods.pop,periods.precipIN,periods.windSpeedMaxMPH,periods.windDirMax,periods.weather,periods.icon&client_id={id}&client_secret={secret}'

CURRENTSAVEFILE = os.environ['HOME'] + '/.config/weather/current.json'
FORECASTSAVEFILE = os.environ['HOME'] + '/.config/weather/forecast.json'

def get_current_weather(location=None, id=None, secret=None, save=True):
    # Check if there is existing data
    try:
        with open(CURRENTSAVEFILE, 'r') as raw_data:
            data = json.load(raw_data)
        if should_update(data.get('timestamp')):
            data = update(CURRENTURL.format(location=location or LOCATION, id=id or ID, secret=secret or SECRET))['response'][0]['periods'][0]
    except FileNotFoundError as e:
        # No file, update
        data = update(CURRENTURL.format(location=location or LOCATION, id=id or ID, secret=secret or SECRET))['response'][0]['periods'][0]
    # Add a timestamp
    data['timestamp'] = round(time.time())
    # Save the file
    if save:
        save_data('current', data)
    return data

def get_forecast(location=None, id=None, secret=None, days=3, save=True):
    try:
        with open(FORECASTSAVEFILE, 'r') as raw_data:
            data = json.load(raw_data)
        if should_update(data.get('timestamp')) or len(data.keys()) - 1 < days:
            data = update(FORECASTURL.format(location=location or LOCATION, id=id or ID, secret=secret or SECRET, days=days))['response'][0]['periods']
    except FileNotFoundError:
        data = update(FORECASTURL.format(location=location or LOCATION, id=id or ID, secret=secret or SECRET, days=days))['response'][0]['periods']
    if isinstance(data, list):
        # Convert the list to a dict
        f_day = 1
        temp_data = {}
        for f_cast in data:
            temp_data['day_{}'.format(f_day)] = f_cast
            f_day += 1
        temp_data['timestamp'] = round(time.time())
        data = temp_data
    if save:
        save_data('forecast', data)
    return data

def update(url):
    data = json.loads(requests.get(url).content)
    return data

def should_update(timestamp, delay=None):
    delay = delay or DELAY
    if timestamp + delay <= time.time():
        return True
    return False

def save_data(cur_fore, data):
        if not isinstance(data, dict):
            return False
        if cur_fore == 'current':
            datafile = CURRENTSAVEFILE
        elif cur_fore == 'forecast':
            datafile = FORECASTSAVEFILE
        else:
            return False
        with open(datafile, 'w') as d:
            json.dump(data, d, indent=4)
        return True

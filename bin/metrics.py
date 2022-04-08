#!/usr/bin/python
import os
import json
import datetime
from pytz import timezone
from pylab import *
from subprocess import call
import numpy as np
import matplotlib.patches as mpatches

PATH_CHART_ROOT = '/var/www/statmap/data/localcharts/'
PATH_STATS_ROOT = '/var/www/statmap/data/stats/'
DateCountyList = []
AllStateCodes = {}

TOTAL_COUNTIES = 3143

json_list = os.listdir(PATH_STATS_ROOT)
json_list = [json_name for json_name in json_list if 'counties.2' in json_name and 'swp' not in json_name]
json_list.sort()

last_date = json_list[-1].split('.')[1]
year = last_date[0:2]
month = last_date[2:4]
day = last_date[4:6]
human_last_date = f'{month}/{day}/{year}'


for json_name in json_list:

    date_code = json_name.split('.')[1]
    countyDict = {}

    path_json = PATH_STATS_ROOT + json_name
    counties_with_cases = 0
    counties_with_deaths = 0

    with open(path_json,'r') as fd:
        config  = json.load(fd)
        counties = config['counties']

        for county in counties:
            state_code = county["state"]
            county_name = county["name"]
            cases = county["cases"]
            deaths = county["deaths"]

            if deaths > 0:
                counties_with_deaths += 1
            if cases > 0:
                counties_with_cases += 1

    print(path_json, counties_with_deaths, counties_with_cases, TOTAL_COUNTIES)
    ratio_cases = (counties_with_cases / TOTAL_COUNTIES) * 100
    ratio_deaths = (counties_with_deaths / TOTAL_COUNTIES) * 100
    print(f'Counties with cases: {ratio_cases}   Counties with deaths: {ratio_deaths}')







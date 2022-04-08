#!/usr/bin/python
import os
import json
import datetime
from pytz import timezone
from pylab import *
from subprocess import call
import numpy as np
import matplotlib.patches as mpatches

PATH_STATS_ROOT= '/var/www/statmap/data/stats/'



daily_list = os.listdir(PATH_STATS_ROOT)
daily_list.sort()
for county_file in daily_list:
    if 'counties.20' not in county_file:
        continue
    path_county_json = PATH_STATS_ROOT + county_file

    total_deaths = 0
    total_cases= 0
    with open(path_county_json,'r') as fd:
        config  = json.load(fd)
        counties = config['counties']
        for county in counties:
            code = county['code']
            cases = county['cases']
            deaths = county['deaths']

            total_deaths += deaths
            total_cases += cases


    print(path_county_json, total_cases, total_deaths)






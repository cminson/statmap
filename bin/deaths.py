#!/usr/bin/python
import os
import json
import datetime
import calendar
from pytz import timezone
from pylab import *
from subprocess import call
import numpy as np
import matplotlib.patches as mpatches

PATH_STATS_ROOT= '/var/www/statmap/data/stats/'



daily_list = os.listdir(PATH_STATS_ROOT)
daily_list.sort()
prev_deaths = 0
prev_cases= 0
for world_file in daily_list:
    if 'swp' in world_file: continue
    if 'world' not in world_file:
        continue
    world_json = PATH_STATS_ROOT + world_file

    with open(world_json,'r') as fd:
        config  = json.load(fd)
        stats = config['stats']
        total_cases = stats[0]['cases']
        total_deaths = stats[0]['deaths']
        inc_deaths = total_deaths - prev_deaths
        prev_deaths = total_deaths


    d = world_file.replace('world.','')
    d = d.replace('.json','')

    year = int('20'+d[0:2])
    month = int(d[2:4])
    day = int(d[4:6])

    day = datetime.datetime(year, month, day).weekday()
    day_name = calendar.day_abbr[day]

    print(d, day_name, total_deaths, inc_deaths)






#!/usr/bin/python
import os
import sys
import json

PATH_STATS_ROOT = '/var/www/statmap/data/stats/'
PATH_STATS_ROOT = '/var/www/statmap/data/velocity/'

json_name = sys.argv[1]
path_json = PATH_STATS_ROOT + json_name

total_deaths = 0

print(path_json)
with open(path_json,'r') as fd:

    config  = json.load(fd)
    states = config['states']

    for state in states:

        state_code = state["state"]
        deaths = state["deaths"]
        total_deaths += int(deaths)


print(f'total_deaths: {total_deaths}')





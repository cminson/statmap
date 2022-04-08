#!/usr/bin/python
import os
import sys
import json

PATH_STATS_ROOT = '/var/www/statmap/data/stats/'

json_name = sys.argv[1]
path_json = PATH_STATS_ROOT + json_name

total_cases = 0
total_deaths = 0

total_counties = 0
counties_with_cases = 0
counties_with_deaths = 0

counties_with_high_deaths = 0

print(path_json)
with open(path_json,'r') as fd:

    config  = json.load(fd)
    counties = config['counties']

    for county in counties:

        state_code = county["state"]
        county_name = county["name"]
        county_code = county["code"]

        if county_code == state_code: 
            print("SEEN", county_code)
            continue

        cases = county["cases"]
        deaths = county["deaths"]
        #print(deaths)

        if deaths > 0:
            counties_with_deaths += 1
        if cases > 0:
            counties_with_cases += 1
        if deaths > 100:
            counties_with_high_deaths += 1

        total_cases += int(cases)
        total_deaths += int(deaths)

        total_counties += 1

rate_counties_deaths = (counties_with_deaths/total_counties) * 100
rate_counties_high_deaths = (counties_with_high_deaths/total_counties) * 100
rate_counties_cases = (counties_with_cases/total_counties) * 100

print(f'total cases: {total_cases}  total_deaths: {total_deaths}')
print(f'total counties:: {total_counties}  deaths%: {rate_counties_deaths}  cases%: {rate_counties_cases}')
print(f'total counties with deaths > 100: {rate_counties_high_deaths} {counties_with_high_deaths}')





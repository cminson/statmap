#!/usr/bin/python
import json
import datetime
from pytz import timezone
from subprocess import call
import os
import csv


PATH_ALL_COUNTIES= '/var/www/statmap/data/stats/ALLCOUNTIES.json'
PATH_STATS_ROOT= '/var/www/statmap/data/stats/'
PATH_VELOCITY_ROOT= '/var/www/statmap/data/velocity/'
PATH_COUNTY_CSV = '/var/www/covid-19-data/us-counties.csv'
PATH_ACTIVE_COUNTIES = '/var/www/statmap/data/stats/API.ACTIVE.COUNTIES.json'
PATH_CENSUS_CSV = '/var/www/statmap/data/census/co-est2019-alldata.csv'

NY_COUNTIES = ['New York', 'Kings', 'Bronx', 'Richmond', 'Queens', 'Rockland', 'Nassau', 'Orange', 'Suffolk', 'Westchester']

STATE_CODE_DICT = {"Alaska": "AK", "Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"};

AllCounties = []
DateToCases = {}
CountyPopDict = {}

DeathsCountyDict = {}

print('xfer ...')





# get population numbers
with open(PATH_CENSUS_CSV, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        state = row['STNAME']
        county = row['CTYNAME'].strip()
        county = county.replace('County','')
        county = county.replace('Parish','')
        county = county.replace('Co.','')
        county = county.replace('city','')
        county = county.strip()
        pop = row['POPESTIMATE2018']

        state_code = STATE_CODE_DICT[state]

        key = state_code+'.'+county
        CountyPopDict[key] = int(pop)
        #print(key, pop)


with open(PATH_ALL_COUNTIES,'r') as fd:
    config = json.load(fd)
    AllCounties = config['counties']

    for county in AllCounties:
        code = county['code'].strip()
        state = county['state'].strip()
        name = county['name'].strip()
        state = state.replace(' ', '')
        key = state+'.'+name
        if key not in CountyPopDict:
            print("NOT FOUND:", key)
            continue
        pop = CountyPopDict[key];

        s = "{\"code\": \"%s\", \"state\": \"%s\", \"name\": \"%s\", \"pop\": %s}," % (code, state, name, pop)
        print(s)


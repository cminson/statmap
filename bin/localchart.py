#!/usr/bin/python3
import os
import json
import datetime
from pytz import timezone
from pylab import *
from subprocess import call
import numpy as np
import matplotlib.patches as mpatches
from subprocess import call
from functools import reduce
import matplotlib.dates as mdates


#call([cmd, "-z", "-e", PATH_INKMAP_IMAGE, "-w", "1000", PATH_ACTIVE_SVG])

RUNNING_AVG = 7

MIN_DAYS_OFFSET0301 = 41

PATH_TMP_DEATHS = '/var/www/statmap/httpdocs/data/tmp/deaths.png'
PATH_TMP_WINDOW_DEATHS = '/var/www/statmap/httpdocs/data/tmp/windowdeaths.png'
PATH_TMP_CASES = '/var/www/statmap/httpdocs/data/tmp/cases.png'
PATH_TMP_WINDOW_CASES = '/var/www/statmap/httpdocs/data/tmp/windowcases.png'

PATH_CHART_ROOT = '/var/www/statmap/httpdocs/data/localcharts/'
PATH_STATS_ROOT = '/var/www/statmap/httpdocs/data/stats/'
DateCountyList = []
DateStateList = []
AllStateCodes = {}

STATE_DICT = {
'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi', 'MT': 'Montana', 'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}
STATE_CODE_DICT = {"Alaska": "AK", "Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"};


locator = mdates.MonthLocator()  # every month
fmt = mdates.DateFormatter('%b')


def average(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)


def plot_chart(locale_name, date_code, chart_name, list_days, list_cases, list_deaths, list_window_deaths, list_window_cases):

    base = datetime.datetime.today()
    numdays = len(list_days)
    date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]

    path = PATH_CHART_ROOT + chart_name + '.png'
    print("PLOTTING: ", path)

    title(f'{locale_name} COVID-19 Total Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('')
    ylabel('total deaths')
    date_list.reverse()

    plt.rcParams.update({'font.size': 8})

    X = plt.gca().xaxis
    X.set_major_locator(locator)
    X.set_major_formatter(fmt)
    plt.plot(date_list, list_deaths, linewidth=2, color='red')
    plt.grid()
    plt.savefig(PATH_TMP_DEATHS)
    plt.close()

    title(f'{locale_name} COVID-19 Running 7-Day Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('')
    ylabel('running 7-day average new deaths')
    X = plt.gca().xaxis
    X.set_major_locator(locator)
    X.set_major_formatter(fmt)
    plt.plot(date_list, list_window_deaths, linewidth=2, color='red')

    plt.grid()
    plt.savefig(PATH_TMP_WINDOW_DEATHS)
    plt.close()

    title(f'{locale_name} COVID-19 Total Cases 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('')
    ylabel('total cases')
    X = plt.gca().xaxis
    X.set_major_locator(locator)
    X.set_major_formatter(fmt)
    plt.plot(date_list, list_cases, linewidth=2, color='magenta')
    plt.grid()
    plt.savefig(PATH_TMP_CASES)
    plt.close()

    title(f'{locale_name} COVID-19 Running 7-Day Cases 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('')
    ylabel('running 7-day average new cases')
    X = plt.gca().xaxis
    X.set_major_locator(locator)
    X.set_major_formatter(fmt)
    plt.plot(date_list, list_running_cases, linewidth=2, color='magenta')
    plt.grid()
    plt.savefig(PATH_TMP_WINDOW_CASES)
    plt.close()

    #call(["convert",  PATH_TMP_WINDOW_DEATHS, PATH_TMP_DEATHS, PATH_TMP_CASES, "-append", path])
    call(["convert",  PATH_TMP_DEATHS, PATH_TMP_WINDOW_DEATHS, PATH_TMP_CASES, PATH_TMP_WINDOW_CASES, "-append", path])




json_list = os.listdir(PATH_STATS_ROOT)
json_list = [json_name for json_name in json_list if 'us.2' in json_name and 'swp' not in json_name]
json_list.sort()

last_date = json_list[-1].split('.')[1]
year = last_date[0:2]
month = last_date[2:4]
day = last_date[4:6]
human_last_date = f'{month}/{day}/{year}'

for json_name in json_list:

    date_code = json_name.split('.')[1]
    countyDict = {}
    stateDict = {}

    path_json = PATH_STATS_ROOT + json_name

    with open(path_json,'r') as fd:
        print(path_json)
        config  = json.load(fd)

        counties = config['counties']
        for county in counties:
            state_code = county["state"]
            county_name = county["name"]
            #print(date_code, state_code, county_name, cases, deaths)

            county_code = state_code + '.' + county_name
            county_code = county_code.replace(' ', '').upper()
            #county_code = county_code.replace(' ', '')
            countyDict[county_code] = county

        states = config['states']
        for state in states:
            state_code = state["code"]
            stateDict[state_code] = state
            AllStateCodes[state_code.strip()] = True

        #print(date_code)
        DateCountyList.append(countyDict)
        DateStateList.append(stateDict)

AllCountyCodes = []

for county, county_code in enumerate(DateCountyList[0]):
    AllCountyCodes.append(county_code)


for state_code in AllStateCodes.keys():

    list_days = []
    list_cases = []
    list_deaths = []
    list_running_deaths = []
    list_running_cases = []

    count = 0

    print(state_code)

    for json_dict in DateStateList:
        #print(json_dict)

        count += 1
        if count < MIN_DAYS_OFFSET0301: continue

        state = json_dict[state_code]
        cases = state['cases']
        deaths = state['deaths']
        avg7_deaths = state['avg7_deaths']
        avg7_cases = state['avg7_cases']

        #print(state, count, total_cases, total_deaths, avg7_deaths)
        list_days.append(count-MIN_DAYS_OFFSET0301)
        list_cases.append(cases)
        list_deaths.append(deaths)
        list_running_deaths.append(avg7_deaths)
        list_running_cases.append(avg7_cases)

    locale_name = state_code + ' State'
    locale_name = STATE_DICT[state_code]
    plot_chart(locale_name, human_last_date, state_code, list_days, list_cases, list_deaths, list_running_deaths, list_running_cases)


for county_code in AllCountyCodes:

    list_days = []
    list_cases = []
    list_deaths = []

    list_running_deaths = []

    list_case_window = []
    list_running_cases = []

    count = 0

    for json_dict in DateCountyList:

        county = json_dict[county_code]
        code = county["code"]
        state = county["state"]
        cases = county["cases"]
        deaths = county["deaths"]
        name = county["name"]
        avg7_deaths = county['avg7_deaths']
        avg7_cases = county['avg7_cases']
        count += 1
        if count < MIN_DAYS_OFFSET0301: continue

        list_days.append(count-MIN_DAYS_OFFSET0301)
        list_cases.append(cases)
        list_deaths.append(deaths)
        list_running_deaths.append(avg7_deaths)
        list_running_cases.append(avg7_cases)


    #locale_name = county_code.split('.')[1] + ' County'
    locale_name = name + ' County'
    plot_chart(locale_name, human_last_date, county_code, list_days, list_cases, list_deaths, list_running_deaths, list_running_cases)








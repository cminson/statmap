#!/usr/bin/python
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
import json
import MySQLdb as mdb


#call([cmd, "-z", "-e", PATH_INKMAP_IMAGE, "-w", "1000", PATH_ACTIVE_SVG])

RUNNING_AVG_WINDOW = 7

MIN_DAYS_OFFSET0301 = 41

PATH_TMP_DEATHS = '/var/www/statmap/ndata/tmp/deaths.png'
PATH_TMP_WINDOW_DEATHS = '/var/www/statmap/ndata/tmp/windowdeaths.png'
PATH_TMP_CASES = '/var/www/statmap/ndata/tmp/cases.png'
PATH_TMP_WINDOW_CASES = '/var/www/statmap/ndata/tmp/windowcases.png'
PATH_CHART_ROOT = '/var/www/statmap/ndata/localcharts/'

DateCountyList = []
AllStateCodes = {}

STATE_DICT = {
'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi', 'MT': 'Montana', 'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}

def average(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)


def plot_chart(locale_name, date_code, chart_name, list_days, list_cases, list_deaths, list_window_deaths, list_window_cases):

    path = PATH_CHART_ROOT + chart_name + '.png'
    print("PLOTTING: ", path)

    title(f'{locale_name} COVID-19 Total Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('day')
    ylabel('total deaths')
    plt.plot(list_days, list_deaths, linewidth=3, color='red')
    plt.grid()
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig(PATH_TMP_DEATHS)
    plt.close()

    title(f'{locale_name} COVID-19 Running 7-Day Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('day')
    ylabel('running 7-day average new deaths')
    plt.plot(list_days, list_window_deaths, linewidth=3, color='red')
    plt.grid()
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig(PATH_TMP_WINDOW_DEATHS)
    plt.close()

    title(f'{locale_name} COVID-19 Total Cases 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('day')
    ylabel('total cases')
    plt.plot(list_days, list_cases, linewidth=3, color='magenta')
    plt.grid()
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig(PATH_TMP_CASES)
    plt.close()

    title(f'{locale_name} COVID-19 Running 7-Day Cases 03/01/20 - {date_code}'+'\nwww.statmap.org')
    xlabel('day')
    ylabel('running 7-day average new cases')
    plt.plot(list_days, list_running_cases, linewidth=3, color='magenta')
    plt.grid()
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.savefig(PATH_TMP_WINDOW_CASES)
    plt.close()

    call(["convert",  PATH_TMP_DEATHS, PATH_TMP_WINDOW_DEATHS, PATH_TMP_CASES, PATH_TMP_WINDOW_CASES, "-append", path])


con = mdb.connect('localhost', 'root', '', 'covid19');
cur = con.cursor()
query = "select day from stats ORDER BY id DESC LIMIT 1"
cur.execute(query)
rows = cur.fetchall()
max_day = rows[0][0]

for state_code in STATE_DICT.keys():

    #if state_code != 'OR': continue
    print(state_code)
    list_days = []
    list_cases = []
    list_deaths = []
    list_new_cases = []
    list_new_deaths = []
    list_running_cases = []
    list_running_deaths = []

    for day in range(0, max_day):
        query = f"select total_cases, total_deaths, running_cases, running_deaths from stats where state='{state_code}' and county_name='State Totals' and day='{day}'"
        #print(query)
        cur.execute(query)
        row = cur.fetchall()[0]
        total_cases = row[0]
        total_deaths = row[1]
        running_cases = row[2]
        running_deaths = row[3]

        list_days.append(day-MIN_DAYS_OFFSET0301)
        list_cases.append(total_cases)
        list_deaths.append(total_deaths)
        list_running_cases.append(running_cases)
        list_running_deaths.append(running_deaths)

    #print(list_days, list_cases, list_deaths, list_running_cases, list_running_deaths)
    locale_name = STATE_DICT[state_code]
    human_last_date = "XXX"

    plot_chart(locale_name, human_last_date, state_code, list_days, list_cases, list_deaths, list_running_deaths, list_running_cases)








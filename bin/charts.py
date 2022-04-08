#!/usr/bin/python3
import os
import json
import datetime
from pytz import timezone
from pylab import *
from subprocess import call
import numpy as np
import matplotlib.patches as mpatches
from functools import reduce
import math
import matplotlib.dates as mdates

plt.rcParams.update({'font.size': 8})


PATH_STATS_ROOT= '/var/www/statmap/httpdocs/data/stats/'

PATH_CHART1 = '/var/www/statmap/httpdocs/data/charts/chart1.png'
PATH_CHART2 = '/var/www/statmap/httpdocs/data/charts/chart2.png'
PATH_CHART3 = '/var/www/statmap/httpdocs/data/charts/chart3.png'
PATH_CHART4 = '/var/www/statmap/httpdocs/data/charts/chart4.png'
PATH_CHART5 = '/var/www/statmap/httpdocs/data/charts/chart5.png'
PATH_CHART6 = '/var/www/statmap/httpdocs/data/charts/chart6.png'
PATH_CHART7 = '/var/www/statmap/httpdocs/data/charts/chart7.png'
PATH_CHART8 = '/var/www/statmap/httpdocs/data/charts/chart8.png'
PATH_CHART9 = '/var/www/statmap/httpdocs/data/charts/chart9.png'
PATH_CHART10 = '/var/www/statmap/httpdocs/data/charts/chart10.png'


MIN_DAYS_OFFSET0301 = 41
POP_RED =  186645477
POP_BLUE = 141927496

list_days = []
list_weeks = []
list_us_cases = []
list_us_deaths = []
list_us_death_rates = []
list_us_case_rates = []
list_us_inc_deaths = []
list_us_inc_cases = []
list_us_running_deaths = []
list_us_running_cases = []

list_world_cases = []
list_world_deaths = []
list_world_death_rates = []

list_usworld_cases = []
list_usworld_deaths = []


def average(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)


RUNNING_AVG = 7

#
# compute US stat numbers
#
stats_list = os.listdir(PATH_STATS_ROOT)
stats_list = [stat_name for stat_name in stats_list if 'world.2' in stat_name and 'swp' not in stat_name]
stats_list.sort()
count = 0
week = 0
prev_us_daily_deaths = 0
prev_us_daily_cases = 0
list_death_window = []
list_case_window = []
inc_running_deaths = 0
inc_running_cases = 0
for stat_name in stats_list:
    path_stat_name = PATH_STATS_ROOT + stat_name

    #if stat_name == stats_list[-1]: continue

    count += 1
    if count < MIN_DAYS_OFFSET0301: continue

    with open(path_stat_name,'r') as fd:
        config  = json.load(fd)
        stats = config['stats'][0]
        us_cases = int(stats['cases'])
        us_deaths = int(stats['deaths'])
        inc_deaths = us_deaths - prev_us_daily_deaths
        inc_cases = us_cases - prev_us_daily_cases
        prev_us_daily_deaths = us_deaths
        prev_us_daily_cases = us_cases
        us_rate = (us_deaths / us_cases) * 100
        #rate = "{:.2f}".format(rate)

        list_death_window.append(inc_deaths)
        if len(list_death_window) > RUNNING_AVG:
            list_death_window.pop(0)
       
        list_case_window.append(inc_cases)
        if len(list_case_window) > RUNNING_AVG:
            list_case_window.pop(0)
       
        stats = config['stats'][1]
        world_cases = stats['cases']
        world_deaths = stats['deaths']
        world_rate = (float(world_deaths) / int(world_cases)) * 100

        usworld_cases = (float(us_cases) / float(world_cases)) * 100
        usworld_deaths = (float(us_deaths) / float(world_deaths)) * 100

    
    inc_running_deaths = average(list_death_window)
    inc_running_cases = average(list_case_window)

    list_days.append(count-MIN_DAYS_OFFSET0301)

    list_us_cases.append(us_cases)
    list_us_deaths.append(us_deaths)
    list_us_death_rates.append(us_rate)

    list_world_cases.append(world_cases)
    list_world_deaths.append(world_deaths)
    list_world_death_rates.append(world_rate)
    list_us_inc_deaths.append(inc_deaths)
    list_us_inc_cases.append(inc_cases)

    list_usworld_cases.append(usworld_cases)
    list_usworld_deaths.append(usworld_deaths)

    list_us_running_deaths.append(inc_running_deaths)
    list_us_running_cases.append(inc_running_cases)

#
# compute by per capita numbers for red blue populations
#
POP_USA = 330000000
PER_CAPITA_POP = 100000
PATH_ALL_STATES = '/var/www/statmap/httpdocs/data/ALLSTATES.json'
PATH_ALL_COUNTIES = '/var/www/statmap/httpdocs/data/NEWALLCOUNTIES.json'
StatePoliticsDict = {}
CountyPopDict = {}
CountyPoliticsDict = {}
StatePopDict = {}
list_ratio_days = []
list_redstate_ratios = []
list_bluestate_ratios = []
list_us_ratios = []

with open(PATH_ALL_STATES,'r') as fd:
    config  = json.load(fd)
    states = config['states']
    for state in states:
        code = state['code']
        politics = state['pol']
        pop = state['pop']
        StatePoliticsDict[code] = politics
        StatePopDict[code] = pop


with open(PATH_ALL_COUNTIES,'r') as fd:
    config  = json.load(fd)
    counties = config['counties']
    for county in counties:
        code = county['code']
        pop = county['pop']
        red_blue = county['redblue']
        CountyPopDict[code] = int(pop)
        CountyPoliticsDict[code] = red_blue


json_list = os.listdir(PATH_STATS_ROOT)
json_list = [county_name for county_name in json_list if 'us' in county_name and 'swp' not in county_name]
json_list.sort()

count = 0
for json_file in json_list:

    count += 1
    if count < MIN_DAYS_OFFSET0301: continue

    total_pop_red = 0
    total_pop_blue = 0
    total_deaths_blue = 0
    total_deaths_red = 0
    path_json_file = PATH_STATS_ROOT + json_file
    with open(path_json_file,'r') as fd:
        config  = json.load(fd)
        counties = config['counties']

        for county in counties:
            code = county['code'].replace('x','')
            state = county['state'].replace(' ','')
            deaths = county['deaths']

            #politics = StatePoliticsDict[state]
            politics = CountyPoliticsDict[code]
            pop = CountyPopDict[code]

            if politics == 'red':
                total_deaths_red += deaths
                total_pop_red += pop
            elif politics == 'blue':
                total_deaths_blue += deaths
                total_pop_blue += pop
            else:
                print('ERROR:', politics, state)
                exit()

        list_ratio_days.append(count-MIN_DAYS_OFFSET0301)
        ratio =  (total_deaths_red / total_pop_red) * PER_CAPITA_POP
        list_redstate_ratios.append(ratio)
        ratio =  (total_deaths_blue / total_pop_blue) * PER_CAPITA_POP
        list_bluestate_ratios.append(ratio)
        ratio = ((total_deaths_red + total_deaths_blue) / POP_USA) * PER_CAPITA_POP
        list_us_ratios.append(ratio)


#
# DEV
#
list_avg7_days = []
list_redstate_avg7 = []
list_bluestate_avg7 = []

list_percapita_red = []
list_percapita_blue = []
count = 0
for json_file in json_list:

    count += 1
    if count < MIN_DAYS_OFFSET0301: continue

    total_pop_red = 0
    total_pop_blue = 0
    total_avg7_blue = 0
    total_avg7_red = 0
    total_red_count = 0
    total_blue_count = 0
    path_json_file = PATH_STATS_ROOT + json_file
    print(path_json_file)
    with open(path_json_file,'r') as fd:
        config  = json.load(fd)
        counties = config['counties']

        for county in counties:
            code = county['code'].replace('x','')
            state = county['state'].replace(' ','')
            avg7_deaths = county['avg7_deaths']

            #politics = StatePoliticsDict[code]
            #pop = StatePopDict[code]
            politics = CountyPoliticsDict[code]
            pop = CountyPopDict[code]
            #politics = "red"
            if politics == 'red':
                total_red_count += 1
                total_avg7_red += avg7_deaths
                total_pop_red += pop

            elif politics == 'blue':
                total_blue_count += 1
                total_avg7_blue += avg7_deaths
                total_pop_blue += pop
            else:
                print('ERROR:', politics, state)
                exit()

        avg7_red = (total_avg7_red * 7) / 1490
        avg7_blue = (total_avg7_blue * 7) / 1860
        list_avg7_days.append(count-MIN_DAYS_OFFSET0301)
        list_percapita_red.append(avg7_red)
        list_percapita_blue.append(avg7_blue)



dt_utc = datetime.datetime.now()
dt_pacific = dt_utc.astimezone(timezone('US/Pacific'))
date_code = dt_pacific.strftime("%m/%d/%y")

locator = mdates.MonthLocator()  # every month
fmt = mdates.DateFormatter('%b')

title(f'COVID-19 Weekly Deaths Per 100,000 03/01/20 - {date_code}'+'\nRed/Blue Counties Comparison  [www.statmap.org]')
xlabel('')
ylabel('weekly deaths per 100,000')
numdays = len(list_ratio_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()

X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)

#plt.plot(date_list, list_redstate_avg7, linewidth=2, color='red')
#plt.plot(date_list, list_bluestate_avg7, linewidth=2, color='blue')
list_percapita_red = [ratio + (ratio * 0.050) for ratio in list_percapita_red]
list_percapita_blue = [ratio + (ratio * 0.00) for ratio in list_percapita_blue]
plt.plot(date_list, list_percapita_red, linewidth=2, color='red')
plt.plot(date_list, list_percapita_blue, linewidth=2, color='blue')
plt.grid()
patch_red = mpatches.Patch(color='red', label='Red Counties')
patch_blue = mpatches.Patch(color='blue', label='Blue Counties')
plt.legend(handles=[patch_red, patch_blue])
plt.savefig(PATH_CHART10)
plt.close()


title(f'COVID-19 Total Deaths Per 100,000 03/01/20 - {date_code}'+'\nRed/Blue Counties Comparison [www.statmap.org]')
xlabel('')
ylabel('total deaths per 100,000')
numdays = len(list_ratio_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)

adjusted_red = [ratio + (ratio * 0.011) for ratio in list_redstate_ratios]
adjusted_blue = [ratio + (ratio * 0.00) for ratio in list_bluestate_ratios]
#print(adjusted_red)
plt.plot(date_list, adjusted_red, linewidth=2, color='red')
plt.plot(date_list, adjusted_blue, linewidth=2, color='blue')
#plt.plot(date_list, list_redstate_ratios, linewidth=2, color='red')
#plt.plot(date_list, list_bluestate_ratios, linewidth=2, color='blue')
plt.grid()
patch_red = mpatches.Patch(color='red', label='Red Counties')
patch_blue = mpatches.Patch(color='blue', label='Blue Counties')
plt.legend(handles=[patch_red, patch_blue])
plt.savefig(PATH_CHART6)
plt.close()


title(f'US COVID-19 Daily Incremental Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('new deaths')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.plot(date_list, list_us_inc_deaths, linewidth=2, color='red')
plt.grid()
plt.savefig(PATH_CHART5)
plt.close()
#print(f'{len(date_list)} {len(list_us_inc_deaths)}')



title(f'US COVID-19 Daily Incremental Cases 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('new cases')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.plot(date_list, list_us_inc_cases, linewidth=2, color='magenta')
plt.grid()
plt.savefig(PATH_CHART8)
plt.close()


title(f'US COVID-19 Running 7-Day Average Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('deaths')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.plot(date_list, list_us_running_deaths, linewidth=2, color='red')
plt.grid()
plt.savefig(PATH_CHART7)
plt.close()

title(f'US COVID-19 Running 7-Day Average Cases 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('new cases')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.plot(date_list, list_us_running_cases, linewidth=2, color='magenta')
plt.grid()
plt.savefig(PATH_CHART9)
plt.close()


title(f'US COVID-19 Cumulative Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('deaths')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.plot(date_list, list_us_deaths, linewidth=2, color='red')
plt.grid()
plt.savefig(PATH_CHART2)
plt.close()


title(f'US COVID-19 Cumulative Cases 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('cases')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.ylim(math.floor(min(list_us_cases)), math.ceil(max(list_us_cases))+50000)
plt.plot(date_list, list_us_cases, linewidth=2, color='magenta')
plt.grid()
plt.savefig(PATH_CHART1)
plt.close()


title(f'US COVID-19 Cumulative Death Rates 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('% death rate')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.plot(date_list, list_us_death_rates, linewidth=2, color='red')
plt.plot(date_list, list_world_death_rates, linewidth=2, color='pink')
plt.grid()
axhline(linestyle='solid', y=2.5, linewidth=2, color='black')
yticks( arange(9), ('0.0', '1.0', '2.0', '3.0', '4.0', '5.0', '6.0', '7.0', '8.0'))
patch_us_rate = mpatches.Patch(color='red', label='US Death Rate')
patch_world_rate = mpatches.Patch(color='pink', label='World Death Rate')
patch_reference = mpatches.Patch(color='black', label='1918 Spanish Flu')
plt.legend(handles=[patch_us_rate, patch_world_rate, patch_reference])
plt.savefig(PATH_CHART3)
plt.close()

title(f'US % World COVID-19 Cases & Deaths 03/01/20 - {date_code}'+'\nwww.statmap.org')
xlabel('')
ylabel('% of world')
numdays = len(list_days)
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
date_list.reverse()
X = plt.gca().xaxis
X.set_major_locator(locator)
X.set_major_formatter(fmt)
plt.plot(date_list, list_usworld_cases, linewidth=2, color='magenta')
plt.plot(date_list, list_usworld_deaths, linewidth=2, color='red')
plt.grid()
axhline(linestyle='solid', y=4.25, linewidth=2, color='black')
patch_cases = mpatches.Patch(color='magenta', label='US Cases as % of World Cases')
patch_deaths  = mpatches.Patch(color='red', label='US Deaths as % of World Deaths')
patch_reference  = mpatches.Patch(color='black', label='US is 4.25% World Population')
plt.legend(handles=[patch_cases, patch_deaths, patch_reference])
plt.savefig(PATH_CHART4)
plt.close()









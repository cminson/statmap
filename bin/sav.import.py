#!/usr/bin/python
import json
import datetime
from pytz import timezone
from subprocess import call
import os
import csv
from functools import reduce


PATH_CENSUS_CSV = '/var/www/statmap/data/census/co-est2019-alldata.csv'

PATH_ALL_COUNTIES= '/var/www/statmap/data/ALLCOUNTIES.json'
PATH_STATS_ROOT= '/var/www/statmap/data/stats/'
PATH_COUNTY_CSV = '/var/www/covid-19-data/us-counties.csv'
PATH_STATES_CSV = '/var/www/covid-19-data/us-states.csv'

PATH_ACTIVE_US_DATA = '/var/www/statmap/data/active/API.ACTIVE.USDATA.json'
PATH_PREVACTIVE_US_DATA = '/var/www/statmap/data/active/API.PREVACTIVE.USDATA.json'


AllCounties = []
DateToCountyData = {}
DateToStateData = {}


STATE_DICT = {
'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana',  'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}
AllStates = list(STATE_DICT.keys())

print('importing ...')

def average(lst):
    return reduce(lambda a, b: a + b, lst) / len(lst)


def getConfigDate(path_config):

    try:
        with open(path_config,'r') as fd:
            config = json.load(fd)
            code = config['date_code']
    except:
        code = '200101'

    return code


# get list of all counties, store in global
with open(PATH_ALL_COUNTIES,'r') as fd:
    config = json.load(fd)
    AllCounties = config['counties']


#
# read in imported state csv
# put data into a dict, indexed by date and state code
#
with open(PATH_STATES_CSV, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        state = row['state']
        date = row['date']
        
        if date not in DateToStateData:
            DateToStateData[date] = {}
        DateToStateData[date][state] = row 

#
# read in imported county csv.  
# put data into a dict, indexed by date and county code
#
with open(PATH_COUNTY_CSV, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        date = row['date']
        county = row['county']
        code = 'c' + row['fips']

        if county == 'New York City':
            code = 'c88888'

        if date not in DateToCountyData:
            DateToCountyData[date] = {}
        DateToCountyData[date][code] = row 


#
# iterate county dict, getting county data for each date
# and then writing that data our into our json files
#
RUNNING_AVG = 7 + 1
window_county_dicts_list = [{}]
window_state_dicts_list = [{}]

for k in DateToCountyData.keys():

    terms = k.split('-')
    us_date = f"{terms[1]}/{terms[2]}/{terms[0]}"
    print(us_date)

    date_code = k.replace('2020','20').replace('-','')
    date_code = date_code.replace('2021','21').replace('-','')
    date_code = date_code.replace('2022','22').replace('-','')
    active_county_dict = DateToCountyData[k]
    window_county_dicts_list.append(active_county_dict)
    if len(window_county_dicts_list) > RUNNING_AVG:
        window_county_dicts_list.pop(0)

    path_us_data = PATH_STATS_ROOT + 'us' + '.' + date_code + '.json'

    FH = open(path_us_data, 'w')
    FH.write("{\n")
    s = "\"date_code\": \"%s\",\n" % (date_code)
    FH.write(s);
    s = "\"usdate\": \"%s\",\n" % (us_date)
    FH.write(s);
    FH.write("\"counties\": [\n")

    for county in AllCounties:
        county_code = county['code']
        state = county['state'].replace(' ','')
        name = county['name']
        cases = 0
        deaths = 0

        if county_code in active_county_dict:
            cases = active_county_dict[county_code]['cases']
            deaths = active_county_dict[county_code]['deaths']
        else:
            county_code = 'x' + county_code

        inc_cases = 0
        avg7_cases = 0
        inc_deaths = 0
        avg7_deaths = 0
        inc_cases_list = []
        inc_deaths_list = []
        for i in range(0, len(window_county_dicts_list)):

            if (i + 1) >= len(window_county_dicts_list): break

            prev_county_dict = window_county_dicts_list[i]
            county_dict = window_county_dicts_list[i+1]

            if county_code not in prev_county_dict: continue
            if county_code not in county_dict: continue

            prev_cases = prev_county_dict[county_code]['cases']
            prev_deaths = prev_county_dict[county_code]['deaths']
            current_cases = county_dict[county_code]['cases']
            current_deaths = county_dict[county_code]['deaths']
            inc_cases = int(current_cases) - int(prev_cases)
            inc_deaths = int(current_deaths) - int(prev_deaths)
            inc_cases_list.append(inc_cases)
            inc_deaths_list.append(inc_deaths)
        # end for, average window

        if len(inc_cases_list) > 0: 
            avg7_cases = round(average(inc_cases_list), 2)
        if len(inc_deaths_list) > 0: 
            avg7_deaths = round(average(inc_deaths_list), 2)

        s = "{\"code\": \"%s\", \"state\": \"%s\", \"name\": \"%s\", \"cases\": %s, \"inc_cases\": %s, \"avg7_cases\": %s, \"deaths\": %s, \"inc_deaths\": %s, \"avg7_deaths\": %s}" % (county_code, state, name, cases, inc_cases, avg7_cases, deaths, inc_deaths, avg7_deaths)
        FH.write(s)
        if county != AllCounties[-1]:
            FH.write(",\n")

    # end for AllCounties

    FH.write("\n")
    FH.write("],\n")
    # end for, all counties on a particular date

    # output all state totals
    active_state_dict = DateToStateData[k]
    window_state_dicts_list.append(active_state_dict)
    if len(window_state_dicts_list) > RUNNING_AVG:
        window_state_dicts_list.pop(0)

    FH.write("\"states\": [\n")
    for state in AllStates:

        state_name = STATE_DICT[state]
        cases = 0
        deaths = 0

        if state_name in active_state_dict:
            cases = active_state_dict[state_name]['cases']
            deaths = active_state_dict[state_name]['deaths']

        inc_cases = 0
        avg7_cases = 0
        inc_deaths = 0
        avg7_deaths = 0
        inc_cases_list = []
        inc_deaths_list = []

        for i in range(0, len(window_state_dicts_list)):

            if (i + 1) >= len(window_state_dicts_list): break

            prev_state_dict = window_state_dicts_list[i]
            state_dict = window_state_dicts_list[i+1]

            if state_name not in prev_state_dict: continue
            if state_name not in state_dict: continue

            prev_cases = prev_state_dict[state_name]['cases']
            prev_deaths = prev_state_dict[state_name]['deaths']
            current_cases = state_dict[state_name]['cases']
            current_deaths = state_dict[state_name]['deaths']
            inc_cases = int(current_cases) - int(prev_cases)
            inc_deaths = int(current_deaths) - int(prev_deaths)
            inc_cases_list.append(inc_cases)
            inc_deaths_list.append(inc_deaths)

        # end for, average window
        if len(inc_cases_list) > 0: 
            avg7_cases = round(average(inc_cases_list), 2)
        if len(inc_deaths_list) > 0: 
            avg7_deaths = round(average(inc_deaths_list), 2)

        s = "{\"code\": \"%s\", \"state\": \"%s\", \"name\": \"%s\", \"cases\": %s, \"inc_cases\": %s, \"avg7_cases\": %s, \"deaths\": %s, \"inc_deaths\": %s, \"avg7_deaths\": %s}" % (state, state, state_name, cases, inc_cases, round(avg7_cases,2), deaths, inc_deaths, round(avg7_deaths,2))
        FH.write(s)
        if state != AllStates[-1]:
            FH.write(",\n")

    FH.write("\n")
    FH.write("]\n")
    FH.write("}\n")
    FH.close()


#
# copy the latest and second-latest stat files into the active directory
#
list_stats = [file_name for file_name in os.listdir(PATH_STATS_ROOT) if 'us' in file_name]
list_stats.sort()

stat_latest = PATH_STATS_ROOT + list_stats[-1]
stat_prev_latest = PATH_STATS_ROOT + list_stats[-2]

print("Copying: ",stat_prev_latest, PATH_PREVACTIVE_US_DATA)
print("Copying: ",stat_latest, PATH_ACTIVE_US_DATA)
call(['cp', stat_prev_latest, PATH_PREVACTIVE_US_DATA])
call(['cp', stat_latest, PATH_ACTIVE_US_DATA])

print('done')



#!/usr/bin/python3
import json
import datetime
from pytz import timezone
from subprocess import call
import os
import csv

from pprint import pprint

PATH_ALL_COUNTIES= '/var/www/statmap/httpdocs/data//ALLCOUNTIES.json'
PATH_ALL_STATES= '/var/www/statmap/httpdocs/data//ALLSTATES.json'

PATH_STATS_ROOT= '/var/www/statmap/httpdocs/data/stats/'
PATH_COUNTY_CSV = '/var/www/covid-19-data/us-counties.csv'
PATH_ACTIVE_TOPRANKED = '/var/www/statmap/httpdocs/data/active/TEST.json'
PATH_ACTIVE_TOPRANKED = '/var/www/statmap/httpdocs/data/active/API.TOPRANKED.json'
PATH_STATS = '/var/www/statmap/httpdocs/data/stats/API.STATS.json'


#c24033

NY_COUNTIES = ['New York', 'Kings', 'Bronx', 'Richmond', 'Queens', 'Rockland', 'Nassau', 'Orange', 'Suffolk', 'Westchester']
STATE_CODE_DICT = {"Alaska": "AK", "Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"};
STATE_DICT = {
'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana',  'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}


AllCounties = []
DateToCases = {}
CountyPopDict = {}
StatePopDict = {}

StateCasesDict = {}
state_code_list = list(STATE_DICT.keys())
for code in state_code_list:
    StateCasesDict[code] = 0


#REPORTING_DEATH_THRESHOLD = 3
REPORTING_DEATH_THRESHOLD = 0
POP_USA = 330000000
POP_INTERVAL = 100000
POP_NYC = 8700000

total_cases = 0

list_state_dailydeaths = []
list_state_totaldeaths = []
list_usa_totaldeaths = []
list_state_avgdeaths = []
list_county_totaldeaths = []


file_name_list = os.listdir(PATH_STATS_ROOT)
file_name_list = [file_name for file_name in file_name_list if 'us' in file_name and 'sw' not in file_name]
file_name_list.sort()

AVG_WINDOW = 7

def compute_death_dict(deaths_dict, week_ago_deaths_dict):

    delta_deaths_dict = state_zero_dict()
    for state_code in deaths_dict:
        today_deaths = deaths_dict[state_code]

        week_ago_deaths = week_ago_deaths_dict[state_code]

        if week_ago_deaths == 0:
            delta_deaths_dict[state_code] = 0
        else:
            delta_deaths_dict[state_code] = today_deaths - week_ago_deaths

    return delta_deaths_dict


def compute_county_death_dict(deaths_dict, week_ago_deaths_dict):

    delta_deaths_dict = {}
    for code in deaths_dict:
        (state, name, today_deaths) = deaths_dict[code]

        week_ago_deaths = 0
        if code in week_ago_deaths_dict:
            (state, name, week_ago_deaths) = week_ago_deaths_dict[code]
            #week_ago_deaths = week_ago_deaths_dict[code]

        if week_ago_deaths == 0:
            delta_deaths_dict[code] = (state, name, 0)
        else:
            delta_deaths_dict[code] = (state, name, today_deaths - week_ago_deaths)

    return delta_deaths_dict


def state_zero_dict():

    state_dict = {}
    for state in STATE_DICT:
        state_dict[state] = 0

    return state_dict



#
# compute stats
#
for file_name in file_name_list:

    path_json_file = PATH_STATS_ROOT + file_name
    #print(path_json_file)
    StateDeathsDict = {}
    state_death_dict = {}
    county_death_dict = {}
    total_deaths = 0

    with open(path_json_file,'r') as fd:
        config  = json.load(fd)
        states = config['states']
        counties = config['counties']

        for state in states:
            state_code = state['code']
            state_name = state['name']
            cases = state['cases']
            deaths = state['deaths']
            state_death_dict[state_code] = deaths
            total_deaths += deaths

        list_state_totaldeaths.append(state_death_dict)
        list_usa_totaldeaths.append(total_deaths)

        for county in counties:
            code = county['code']
            if (code == 'AK'):
                print("ERROR")
                exit()
            cases = county['cases']
            deaths = county['deaths']
            name = county['name']
            state = county['state']
            county_death_dict[code] = (state, name, deaths)

        list_county_totaldeaths.append(county_death_dict)
        """
        if 'CO' in state_death_dict:
            deaths = state_death_dict['CO']
            print(deaths)
        """


with open(PATH_ALL_COUNTIES,'r') as fd:
    config  = json.load(fd)
    counties = config['counties']

    for county in counties:
        code = county['code']
        state = county['state'].replace(' ','')
        name = county['name']
        pop = county['pop']
        CountyPopDict[code] = pop
        if state not in StatePopDict:
            StatePopDict[state] = 0
        StatePopDict[state] += pop


with open(PATH_ALL_STATES,'r') as fd:
    config  = json.load(fd)
    states = config['states']

    for state in states:
        code = state['code']
        pop = state['pop']
        #print(code, pop)
        StatePopDict[code] = pop


file_name_list = os.listdir(PATH_STATS_ROOT)
file_name_list = [file_name for file_name in file_name_list if 'us' in file_name and 'sw' not in file_name]
file_name_list.sort()

#
# create json file 
#
for file_name in file_name_list:


    total_deaths = 0
    total_cases = 0
    path_json_file = PATH_STATS_ROOT + file_name

    StateDeathsDict = {}

    state_code_list = list(STATE_DICT.keys())
    for code in state_code_list:
        StateDeathsDict[code] = 0

    with open(path_json_file,'r') as fd:
        config  = json.load(fd)
        states = config['states']
        counties = config['counties']

        #if file_name != 'counties.200403.json': continue

        top_deaths = []
        for county in counties:

            code = county['code']
            if 'x' in code: continue
            name = county['name']
            state = county['state'].replace(' ','')
            state_name = STATE_DICT[state]
            cases = county['cases']
            deaths = county['deaths']


            if state not in StateDeathsDict:
                StateDeathsDict[state] = 0
            StateDeathsDict[state] += deaths
            if state not in StateCasesDict:
                StateCasesDict[state] = 0
            StateCasesDict[state] += cases

            if code not in CountyPopDict:
                print('NO FOUND', code)
                #exit()
            if name == 'New York City': 
                pop = POP_NYC
            else:
                pop = CountyPopDict[code]
            ratio = (POP_INTERVAL / pop) * deaths

            if deaths > REPORTING_DEATH_THRESHOLD:
                ratio = round(ratio, 2)
            else:
                ratio = 0.0

            top_deaths.append((ratio, state, state_name, name,  cases, deaths, code))

        top_deaths.sort()
        top_deaths.reverse()
        #top_deaths = top_deaths[0:10]
        
        top_name = file_name.replace('us','top')
        top_path = PATH_STATS_ROOT + top_name
        if os.path.exists(top_path):
            #print(f"{top_path} Already Exists: Skipping")
            continue


        #
        # output json
        #
        print("New File: ", top_path)
    
        #
        # top_county_deaths
        #
        this_week_deaths_dict = compute_county_death_dict(list_county_totaldeaths[-1], list_county_totaldeaths[-8])
        prev_week_deaths_dict = compute_county_death_dict(list_county_totaldeaths[-8], list_county_totaldeaths[-15])


        FH = open(top_path, 'w')

        FH.write("{\n")
        FH.write("\"top_county_deaths\": [\n")
        for record in top_deaths:
            ratio = record[0]
            state = record[1]
            state_name = record[2]
            name = record[3]
            cases = record[4]
            deaths = record[5]
            code = record[6]

            total_cases += int(cases)
            total_deaths += int(deaths)

            trend = 'flat'
            #print(this_week_deaths_dict)
            if code not in this_week_deaths_dict: 
                this_week_deaths_dict[code] = (code, name, deaths)
            this_weeks_deaths = this_week_deaths_dict[code]
        

            prev_weeks_deaths = (state, name, 0)
            if code in prev_week_deaths_dict:
                prev_weeks_deaths = prev_week_deaths_dict[code]
            else:
                #print(prev_weeks_deaths, this_weeks_deaths)
                print('County Not Found: ', code)

            if this_weeks_deaths > prev_weeks_deaths: trend = 'up'
            if this_weeks_deaths < prev_weeks_deaths: trend = 'down'

            s = "{\"code\": \"%s\",  \"state_name\": \"%s\", \"name\": \"%s\", \"cases\": %s, \"deaths\": %s, \"ratio\": %s, \"trend\": \"%s\"}," % (state, state_name, name, cases, deaths, ratio, trend)
            FH.write(s)
            FH.write("\n")

        ratio = (POP_INTERVAL / POP_USA) * total_deaths
        ratio = round(ratio, 2)
        s = "{\"code\": \"%s\",  \"state_name\": \"%s\", \"name\": \"%s\", \"cases\": %s, \"deaths\": %s, \"ratio\": %s, \"trend\": \"%s\"}" % ('USA', 'USA', 'Average', total_cases, total_deaths, ratio, trend)
        FH.write(s)
        FH.write("\n")
        FH.write("\n")
        FH.write("],\n")

        #
        # top_state_deaths
        #
        top_deaths = []
        for state, deaths in StateDeathsDict.items():
            pop = StatePopDict[state]
            ratio = (POP_INTERVAL / pop) * deaths
            ratio = round(ratio, 2)
            top_deaths.append((ratio, state, deaths))

        this_week_deaths_dict = compute_death_dict(list_state_totaldeaths[-1], list_state_totaldeaths[-8])
        prev_week_deaths_dict = compute_death_dict(list_state_totaldeaths[-8], list_state_totaldeaths[-15])
        this_week_usa_deaths = list_usa_totaldeaths[-1] - list_usa_totaldeaths[-8]
        prev_week_usa_deaths = list_usa_totaldeaths[-8] - list_usa_totaldeaths[-15]

        top_deaths.sort()
        top_deaths.reverse()
        #top_deaths = top_deaths[0:10]
        FH.write("\"top_state_deaths\": [\n")
        for record in top_deaths:
            ratio = record[0]
            state = record[1]
            deaths = record[2]
            state_name = STATE_DICT[state]
            cases = StateCasesDict[state]

            this_weeks_deaths = this_week_deaths_dict[state]
            prev_weeks_deaths = prev_week_deaths_dict[state]

            trend = 'flat'
            if this_weeks_deaths > prev_weeks_deaths: trend = 'up'
            if this_weeks_deaths < prev_weeks_deaths: trend = 'down'

            s = "{\"code\": \"%s\",  \"state_name\": \"%s\", \"cases\": %s, \"deaths\": %s, \"ratio\": %s, \"trend\": \"%s\"}," % (state, state_name, cases, deaths, ratio, trend)

            FH.write(s)
            FH.write("\n")

        usa_trend = 'flat'
        if this_week_usa_deaths > prev_week_usa_deaths: usa_trend = 'up'
        if this_week_usa_deaths < prev_week_usa_deaths: usa_trend = 'down'

        ratio = (POP_INTERVAL / POP_USA) * total_deaths
        ratio = round(ratio, 2)
        s = "{\"code\": \"%s\",  \"state_name\": \"%s\", \"name\": \"%s\", \"cases\": %s, \"deaths\": %s, \"ratio\": %s, \"trend\": \"%s\"}" % ('Average, USA', 'Average, USA', 'Average', total_cases, total_deaths, ratio, usa_trend)
        FH.write(s)
        FH.write("\n")

        FH.write("],\n")


        todays_deaths_dict = list_state_totaldeaths[-1]

        this_week_deaths_dict = compute_death_dict(list_state_totaldeaths[-1], list_state_totaldeaths[-8])
        prev_week_deaths_dict = compute_death_dict(list_state_totaldeaths[-9], list_state_totaldeaths[-16])
        delta_list = []

        for state, this_weeks_deaths in this_week_deaths_dict.items():

            pop = StatePopDict[state]

            delta =  (POP_INTERVAL / pop) * this_weeks_deaths
            if delta < 0.0: delta = 0.0
            delta = round(delta, 2)

            prev_weeks_deaths = prev_week_deaths_dict[state]
            prev_delta =  (POP_INTERVAL / pop) * prev_weeks_deaths
            if prev_delta < 0.0: prev_delta = 0.0
            prev_delta = round(prev_delta, 2)

            delta_list.append((state, delta, prev_delta))

        delta_list.sort(key=lambda x:x[1])
        delta_list.reverse()

        #
        # state deltas 7-day
        #
        this_week_deaths_dict = compute_county_death_dict(list_county_totaldeaths[-1], list_county_totaldeaths[-8])
        county_delta_list = []
        #print(this_week_deaths_dict)
        for county, county_stats in this_week_deaths_dict.items():

            if 'x' in county: continue

            state = county_stats[0]
            name = county_stats[1]
            this_weeks_deaths = county_stats[2]

            pop = CountyPopDict[county]
            delta =  (POP_INTERVAL / pop) * this_weeks_deaths
            if delta < 0.0: delta = 0.0
            delta = round(delta, 2)
            county_delta_list.append((county, state, name, delta))

        county_delta_list.sort(key=lambda x:x[3])
        county_delta_list.reverse()

        FH.write("\"top_state_deltas\": [\n")
        for index, record in enumerate(delta_list):
            code = record[0]
            state_name = STATE_DICT[code]
            rate = record[1]
            prev_rate = record[2]

            s = "{\"code\": \"%s\", \"state_name\": \"%s\", \"rate\": %s, \"prev_rate\": %s}," % (code, state_name, rate,prev_rate)
            FH.write(s)
            FH.write("\n")

        delta_usa_deaths =  (POP_INTERVAL / POP_USA) * this_week_usa_deaths
        prev_delta_usa_deaths =  (POP_INTERVAL / POP_USA) * prev_week_usa_deaths
        delta_usa_deaths = round(delta_usa_deaths, 2)
        prev_delta_usa_deaths = round(prev_delta_usa_deaths, 2)

        s = "{\"code\": \"%s\", \"state_name\": \"%s\", \"rate\": %s, \"prev_rate\": %s}" % ('USA', 'USA', delta_usa_deaths, prev_delta_usa_deaths)
        FH.write(s)
        FH.write("\n")

        FH.write("],\n")


        #
        # county deltas 7-day
        #
        FH.write("\"top_county_deltas\": [\n")
        for index, record in enumerate(county_delta_list):
            code = record[0]
            state = record[1]
            name = record[2]
            rate = record[3]

            s = "{\"code\": \"%s\", \"state_name\": \"%s\", \"name\": \"%s\", \"rate\": %s}," % (code, state, name, rate)
            FH.write(s)
            FH.write("\n")

        delta_usa_deaths =  (POP_INTERVAL / POP_USA) * this_week_usa_deaths
        prev_delta_usa_deaths =  (POP_INTERVAL / POP_USA) * prev_week_usa_deaths
        delta_usa_deaths = round(delta_usa_deaths, 2)
        prev_delta_usa_deaths = round(prev_delta_usa_deaths, 2)
        s = "{\"code\": \"%s\", \"state_name\": \"%s\", \"rate\": %s, \"prev_rate\": %s}" % ('USA', 'USA', delta_usa_deaths, prev_delta_usa_deaths)
        FH.write(s)
        FH.write("\n")
        FH.write("]\n")

        FH.write("}\n")
        FH.close()


#
# copy the LAST (latest) report to the ACTIVE repot
# this is the json file that the user will see
#
print("Deploying: ",top_path, PATH_ACTIVE_TOPRANKED)
call(['cp', top_path, PATH_ACTIVE_TOPRANKED])

print('done')



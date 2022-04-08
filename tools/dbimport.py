#!/usr/bin/python
import json
import datetime
from pytz import timezone
from subprocess import call
import os
import csv

PATH_IMPORTED_DATA = '/var/www/covid-19-data/us-counties.csv'
PATH_COUNTY_DEMOGRAPHICS= '/var/www/statmap/ndata/demographics/ALLCOUNTIES.json'

PATH_COUNTIES_ROOT= '/var/www/statmap/ndata/counties/'
PATH_DELTA_ROOT= '/var/www/statmap/ndata/delta/'
PATH_ACTIVE_COUNTIES = '/var/www/statmap/ndata/active/API.ACTIVE.COUNTIES.json'
PATH_PREVACTIVE_COUNTIES = '/var/www/statmap/ndata/active/API.PREVACTIVE.COUNTIES.json'
PATH_CENSUS_CSV = '/var/www/statmap/ndata/demographics/co-est2019-alldata.csv'


AllCounties = []
DateToCases = {}
CountyPopDict = {}

DeathsCountyDict = {}
PrevDict = {}

print('importing ...')

def getConfigDate(path_config):

    us_date = '01/01/2020'
    try:
        with open(path_config,'r') as fd:
            config = json.load(fd)
            us_date = config['usdate']
    except:
        us_date = '01/01/2020'

    us_date = us_date.replace('2020','20')
    terms = us_date.split('/')
    code = f'{terms[2]}{terms[0]}{terms[1]}'
    return code

# store off template of county data
with open(PATH_COUNTY_DEMOGRAPHICS,'r') as fd:
    config = json.load(fd)
    AllCounties = config['counties']

    for county in AllCounties:
        name = county['name'].strip()
        state = county['state'].strip()

        key = state+'.'+name
        print(key)
        DeathsCountyDict[key] = 0


#
# read in imported county csv.  
# put data into a dict, indexed by date and county code
#
with open(PATH_IMPORTED_DATA, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        date = row['date']
        county = row['county']
        state = row['state']
        code = 'c' + row['fips']
        cases = row['cases']
        deaths = row['deaths']

        if county == 'New York City':
            code = 'c88888'

        if date not in DateToCases:
            DateToCases[date] = {}
        DateToCases[date][code] = row 

#
# iterate that dict, getting county data for each date
# and then writing that data our into our json files
#
for k in DateToCases.keys():


    terms = k.split('-')
    datecode = k.replace('-','')
    us_date = f"{terms[1]}/{terms[2]}/{terms[0]}"

    code = k.replace('2020','20').replace('-','')
    active_county_dict = DateToCases[k]
    path_county_stats = PATH_COUNTIES_ROOT + 'counties' + '.' + code + '.json'
    print(path_county_stats)
    FH = open(path_county_stats, 'w')
    FH.write("{\n")
    s = "\"datecode\": \"%s\",\n" % (datecode)
    FH.write(s);
    s = "\"usdate\": \"%s\",\n" % (us_date)
    FH.write(s);
    FH.write("\"counties\": [\n")
    for county in AllCounties:
        code = county['code']
        state = county['state']
        name = county['name']
        cases = 0
        deaths = 0
        new_cases = 0
        new_deaths = 0

        if code in active_county_dict:
            cases = active_county_dict[code]['cases']
            deaths = active_county_dict[code]['deaths']

            if code in PrevDict:
                prev_cases = PrevDict[code][0]
                prev_deaths = PrevDict[code][1]
                new_cases = int(cases) - int(prev_cases)
                new_deaths = int(deaths) - int(prev_deaths)

            PrevDict[code] = (cases, deaths)
        else:
            code = 'x' + code

        s = "{\"code\": \"%s\", \"state\": \"%s\", \"name\": \"%s\", \"cases\": %s, \"new_cases\": %s, \"deaths\": %s, \"new_deaths\": %s}" % (code, state, name, cases, new_cases, deaths, new_deaths)
        FH.write(s)
        if county != AllCounties[-1]:
            FH.write(",\n")


    FH.write("\n")
    FH.write("]\n")
    FH.write("}\n")
    FH.close()

#
# copy the LAST (latest) county to the ACTIVE county
# this is the json file that the user will see
#
new_config_date = getConfigDate(path_county_stats)
active_config_date = getConfigDate(PATH_ACTIVE_COUNTIES)
print(new_config_date, active_config_date)
if new_config_date > active_config_date:
    print("Backing up Previous: ",PATH_ACTIVE_COUNTIES, PATH_PREVACTIVE_COUNTIES)
    print("Copying: ",path_county_stats, PATH_ACTIVE_COUNTIES)
    call(['cp', PATH_ACTIVE_COUNTIES, PATH_PREVACTIVE_COUNTIES])
    call(['cp', path_county_stats, PATH_ACTIVE_COUNTIES])
else:
    print("No Installation: ",path_county_stats, PATH_ACTIVE_COUNTIES)




print('done')



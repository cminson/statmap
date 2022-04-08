#!/usr/bin/python3

import os
import sys
import json
import string
import json
import operator
import re, math
import time
import datetime
from datetime import date
from pytz import timezone

from subprocess import call
from collections import Counter
import urllib.request
from bs4 import BeautifulSoup

#DELTA = 3025 + 1700
DELTA = 4975
DELTA = 4925
DELTA = 5125
DELTA = 5186
DELTA_CASES = 175135

def getConfigDate(path_config):

    us_date = '01/01/2020'
    try:
        with open(path_config,'r') as fd:
            config = json.load(fd)
            us_date = config['usdate']
    except:
        us_date = '01/01/2020'

    us_date = us_date.replace('2021','21')
    terms = us_date.split('/')
    code = f'{terms[2]}{terms[0]}{terms[1]}'
    return code

dt_utc = datetime.datetime.now()
dt_pacific = dt_utc.astimezone(timezone('US/Pacific'))
date_code = dt_pacific.strftime("%y%m%d")

PATH_STATS_ROOT= '/var/www/statmap/httpdocs/data/stats/'
PATH_ACTIVE_STATS = '/var/www/statmap/httpdocs/data/active/API.WORLD.json'
PATH_PREVACTIVE_STATS = '/var/www/statmap/httpdocs/data/active/API.PREVACTIVE.WORLD.json'
PATH_CANDIDATE_STATS = '/var/www/statmap/httpdocs/data/tmp/candidate.json'
PATH_ARCHIVED_STATS = '/var/www/statmap/httpdocs/data/stats/world.' + date_code + '.json'


call(['wget', '-O', '/var/www/statmap/httpdocs/data/tmp/worldmeter.html', 'https://www.worldometers.info/coronavirus/'])
f=open("/var/www/statmap/httpdocs/data/tmp/worldmeter.html", "r")
html = f.read()

soup = BeautifulSoup(html, 'html.parser')
title = soup.find('title')
title = title.string
words = title.split()
print(words)
print('HERE', words[5])
cases_world = words[3].replace(',','')
deaths_world = words[6].replace(',','')
print(cases_world, deaths_world)


s = str(html)
index = s.find('USA')
substring = s[index+20:index+350]
print(substring)
substring = substring.replace(' ', '')
substring = substring.replace('>', ' ')
substring = substring.replace('<', ' ')
print(substring)
pieceList = substring.split(' ')

for i,piece in enumerate(pieceList):
    print(i, piece)

cases_usa = int(pieceList[1].replace(',',''))
deaths_usa = int(pieceList[9].replace(',',''))
deaths_usa = deaths_usa - DELTA
cases_usa = cases_usa - DELTA_CASES
print(cases_usa, deaths_usa)

#CJM DEV
#deaths_world = int(deaths_world) - (1 * DELTA)
#cases_world = int(cases_world) - (2 * DELTA_CASES)
cases_world = 273162387
deaths_world = 5351703

today = date.today()
us_date = today.strftime("%m/%d/%y")

# outpuy stats to candidate json
FH = open(PATH_CANDIDATE_STATS, 'w')
FH.write("{\n")
s = "\"usdate\": \"%s\",\n" % (us_date)
#FH.write(s);
FH.write("\"stats\": [\n")

s = "{\"area\": \"US\", \"cases\": %s, \"deaths\": %s},\n" % (cases_usa, deaths_usa)
print(s)
FH.write(s)
s = "{\"area\": \"WORLD\", \"cases\": %s, \"deaths\": %s}\n" % (cases_world, deaths_world)
FH.write(s)

FH.write("]\n")
FH.write("}\n")
FH.close()


# validate this json
# exit if bad
try:
    with open(PATH_CANDIDATE_STATS,'r') as myfile:
        data  = json.load(myfile)
        #print(data)
        print("{}: JSON Valid".format(PATH_CANDIDATE_STATS))
except ValueError as e:
    print(e)
    print("{}: Bad JSON!".format(PATH_CANDIDATE_STATS))
    exit(0)
except:
    e = sys.exc_info()[0]
    print(e)
    print("{}: Bad JSON!".format(PATH_CANDIDATE_STATS))
    exit(0)


#
# the data is good, so archive
# this stat data into PATH_ARCHIVED_STATS
#
print(f'Archiving: {PATH_CANDIDATE_STATS} to {PATH_ARCHIVED_STATS}')
call(['cp', PATH_CANDIDATE_STATS, PATH_ARCHIVED_STATS])

#
# now activate new stats:
# copy the latest archived stats into PATH_ACTIVE_STATS
# copy the second latest archived stats into PATH_PREVACTIVE_STATS
#
list_stats = [PATH_STATS_ROOT + file_name for file_name in os.listdir(PATH_STATS_ROOT) if 'world' in file_name]
list_stats.sort()
stat_latest = list_stats[-1]
stat_prev_latest = list_stats[-2]

# copy new stats to active directory
print(f'Deploying: {stat_latest} to {PATH_ACTIVE_STATS}')
call(['cp', stat_latest, PATH_ACTIVE_STATS])
print(f'Deploying: {stat_prev_latest} to {PATH_PREVACTIVE_STATS}')
call(['cp', stat_prev_latest, PATH_PREVACTIVE_STATS])







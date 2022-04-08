#!/usr/bin/python

import os
import sys
from subprocess import call


PATH_STATS_ROOT= '/var/www/statmap/data/stats/'
PATH_ACTIVE_US_DATA = '/var/www/statmap/data/active/API.ACTIVE.USDATA.json'
PATH_PREVACTIVE_US_DATA = '/var/www/statmap/data/active/API.PREVACTIVE.USDATA.json'


list_stats = []
for f in  os.listdir(PATH_STATS_ROOT):
    if 'us' in f:
        list_stats.append(PATH_STATS_ROOT + f)

list_stats.sort()

for f in list_stats:
    print(f)

stat_latest = list_stats[-1]
stat_prev_latest = list_stats[-2]

print("Copying: ",stat_prev_latest, PATH_PREVACTIVE_US_DATA)
print("Copying: ",stat_latest, PATH_ACTIVE_US_DATA)
call(['cp', stat_prev_latest, PATH_PREVACTIVE_US_DATA])
call(['cp', stat_latest, PATH_ACTIVE_US_DATA])


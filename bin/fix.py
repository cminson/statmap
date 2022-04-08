#!/usr/bin/python

import os
import sys
import json
import string
import json

PATH_SOURCE = '/var/www/statmap/data/save/'
PATH_DEV = '/var/www/statmap/data/dev/'
FIX_DEATHS = 15
FIX_CASES = 1000

FixDeathsAmount = 0
FixCasesAmount = 0

world_files = os.listdir(PATH_SOURCE)
world_files.sort()

count = 0
for world_file in world_files:
    count += 1
    if count < 100: continue

    path_source_file = PATH_SOURCE + world_file
    path_dev_file = PATH_DEV + world_file
    print(path_source_file)

    FixDeathsAmount += FIX_DEATHS
    FixCasesAmount += FIX_CASES
    with open(path_source_file,'r') as fd:
        config  = json.load(fd)
        stats = config['stats'][0]

        us_date = config['usdate']

        cases_usa = int(stats['cases'])
        deaths_usa = int(stats['deaths'])

        deaths_usa = deaths_usa - FixDeathsAmount
        cases_usa = cases_usa - FixCasesAmount
        stats = config['stats'][1]
        cases_world = int(stats['cases'])
        deaths_world = int(stats['deaths'])
        print(us_date, cases_usa, deaths_usa, cases_world, deaths_world)

    
    print(FixDeathsAmount)

    FH = open(path_dev_file, 'w')
    FH.write("{\n")
    #s = "\"usdate\": \"%s\",\n" % (us_date)
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
"""
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


"""





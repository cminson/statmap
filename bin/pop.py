#!/usr/bin/python
import os
import sys
import json

PATH_STATES = '/var/www/statmap/data/ALLSTATES.json'


total_cases = 0
total_deaths = 0

pop_red = 0
pop_blue = 0

with open(PATH_STATES,'r') as fd:

    config  = json.load(fd)
    states = config['states']

    for state in states:

        state_name = state["name"]
        pop = state["pop"]
        pol = state["pol"]

        print(pop, pol, state_name)
        if pol == 'red':
            pop_red += int(pop)
        elif pol == 'blue':
            pop_blue += int(pop)
        else:
            print('ERROR: ', state_name)
            break


print(f'red pop: {pop_red}  blue_pop: {pop_blue}')





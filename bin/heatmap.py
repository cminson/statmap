#!/usr/bin/python3
import json
import datetime
import os
from pytz import timezone
from subprocess import call
import sys


PATH_STATS_ROOT= '/var/www/statmap/httpdocs/data/stats/'
PATH_ALL_COUNTIES= '/var/www/statmap/httpdocs/data/ALLCOUNTIES.json'

PATH_TMP = '/var/www/statmap/httpdocs/data/tmp/'
PATH_MAPS = '/var/www/statmap/httpdocs/data/maps/'
PATH_ACTIVE_MAP = '/var/www/statmap/httpdocs/data/maps/heatmap.png'
PATH_ACTIVE_HOTZONEMAP = '/var/www/statmap/httpdocs/data/maps/hotzone.png'
PATH_INKMAP_IMAGE = PATH_TMP+'inkmap.png'
PATH_BASE_SVG = '/var/www/statmap/httpdocs/data/svg/newbasemap.svg'
PATH_ACTIVE_SVG = '/var/www/statmap/httpdocs/data/svg/activemap.svg'

COLOR_SIMMER = '{fill: #FFC0CB}'
COLOR_LOW = '{fill: #e75480}'
COLOR_MEDIUM = '{fill: #a00000}'
COLOR_HOT = '{fill: #ff0000}'

PER_CAPITA_LOW = 50
PER_CAPITA_MEDIUM = 250
PER_CAPITA_HOT = 500

POP_INTERVAL = 100000
POP_NYC = 8700000
CountyPopDict = {}

MIN_DAYS_OFFSET0301 = 41


#
# generate total per capita deaths heatmap
#
def genHeatMap(county_file, frame_count, date_code, deaths):

    #print('genHeatMap', county_file, frame_count)

    #map_file = date_code + '.0.' + 'heatmap.png'
    map_file = date_code + '.' + str(frame_count) + '.' + 'heatmap.png'
    path_output = PATH_MAPS + map_file

    print("Processing: ", path_output)
    if os.path.exists(path_output):
        print('SKIPPING - OUTPUT EXISTS: ', path_output)
        return

    path_county_json = PATH_STATS_ROOT + county_file
    print(path_county_json)
    with open(path_county_json,'r') as fd:
        config  = json.load(fd)
        date_label = config['usdate']
        counties = config['counties']

    activeSVG_FD = open(PATH_ACTIVE_SVG,'w')
    with open(PATH_BASE_SVG, 'r') as fd:

        map_lines = fd.readlines()
        for line in map_lines:
            activeSVG_FD.write(line)
            if '<style' in line:
                for county in counties:
                    code = county['code']
                    name = county['name']
                    state = county['state']

                    # filter 1) counties with no activity and 2) states
                    if 'x' in code: continue
                    if code == state: continue

                    county_deaths = 0
                    if 'deaths' in county:
                        county_deaths = int(county['deaths'])

                    if name == 'New York City':
                        pop = POP_NYC
                    else:
                        pop = CountyPopDict[code]

                    ratio = (POP_INTERVAL / pop) * county_deaths
                    #print(name, ratio)

                    if county_deaths < PER_CAPITA_LOW:
                        fill_code = COLOR_SIMMER
                    elif ratio < PER_CAPITA_MEDIUM:
                        fill_code = COLOR_LOW
                    else:
                        fill_code = COLOR_HOT

                    style = '#' + code + ' ' + fill_code

                    activeSVG_FD.write(style)
                    activeSVG_FD.write('\n')
                continue
    activeSVG_FD.close()
    fd.close()
    
    cmd = "inkscape"
    call([cmd, "-z", "-e", PATH_INKMAP_IMAGE, "-w", "1000", PATH_ACTIVE_SVG])

    #label = f"{date_label}\n{deaths:,d} deaths"
    label = f"Total Deaths\n{deaths:,d}"
    path_input = PATH_INKMAP_IMAGE
    path_output = PATH_TMP+'label1.png'
    call(['convert', path_input, "-gravity", "North", "-background", "white", "-fill", "black", "-splice", "0x50", "-pointsize", "28",  "-font", "Helvetica-Bold", "-annotate", "+0+30", label, path_output])

    label = f"COVID-19 Total Per Capita Deaths\n{date_label}"
    path_input = path_output
    path_output = PATH_TMP+'label2.png'
    call(['convert', path_input, "-gravity", "North", "-background", "white", "-fill", "black", "-splice", "0x90", "-pointsize", "28",  "-font", "Helvetica", "-annotate", "+0+45", label, path_output])

    label = f"Pink=Deaths < {PER_CAPITA_LOW} per 100,000   Dark Pink=Deaths < {PER_CAPITA_MEDIUM} per 100,000   Bright Red=Deaths > {PER_CAPITA_MEDIUM} per 100,000 population\nwww.statmap/httpdocs.org"
    path_input = path_output
    path_output = PATH_TMP+'label3.png'
    call(['convert', path_input, "-gravity", "South", "-background", "white", "-fill", "black", "-splice", "0x90", "-pointsize", "14",  "-font", "Helvetica", "-annotate", "+0+45", label, path_output])

    path_input = path_output
    map_file = date_code + '.' + str(frame_count) + '.' + 'heatmap.png'
    path_output = PATH_MAPS + map_file
    call(['convert', '-flatten', '-resize', '1000x864!', path_input, path_output])
    print(f"Map Installed: {path_output}")

    return path_output


#
# generate incremental per capita daily deaths heatmap (hotzone)
#
def genHotZoneMap(county_file, frame_count, date_code, deaths):

    print('genHotZoneMap', county_file, frame_count)

    map_file = date_code + 'hotzone.png'
    path_output = PATH_MAPS + map_file
    print(path_output)

    """
    if os.path.exists(path_output):
        print('SKIPPING - OUTPUT EXISTS: ', path_output)
        return
    """

    path_county_json = PATH_STATS_ROOT + county_file
    print(path_county_json)
    with open(path_county_json,'r') as fd:
        config  = json.load(fd)
        date_label = config['usdate']
        counties = config['counties']

    activeSVG_FD = open(PATH_ACTIVE_SVG,'w')
    with open(PATH_BASE_SVG, 'r') as fd:

        map_lines = fd.readlines()
        for line in map_lines:
            activeSVG_FD.write(line)
            if '<style' in line:
                for county in counties:
                    code = county['code']
                    state = county['state']
                    name = county['name']
                    avg7_deaths = county['avg7_deaths']

                    # filter 1) counties with no activity and 2) states 
                    if 'x' in code: continue
                    if code == state: continue
                    #if code != 'c41033': continue

                    if name == 'New York City':
                        pop = POP_NYC
                    else:
                        pop = CountyPopDict[code]

                    if avg7_deaths == 0: continue

                    ratio = avg7_deaths / pop
                    if ratio > (1 / 100000):
                        fill_code = COLOR_HOT
                    elif ratio > (1 / 500000):
                        fill_code = COLOR_LOW
                    else:
                        fill_code = COLOR_SIMMER

                    style = '#' + code + ' ' + fill_code

                    activeSVG_FD.write(style)
                    activeSVG_FD.write('\n')
                continue
    activeSVG_FD.close()
    fd.close()
    
    cmd = "inkscape"
    call([cmd, "-z", "-e", PATH_INKMAP_IMAGE, "-w", "1000", PATH_ACTIVE_SVG])

    label = f"COVID-19 Hot Zones as of {date_label}"
    #path_input = path_output
    path_input = PATH_INKMAP_IMAGE
    path_output = PATH_TMP+'label2.png'
    call(['convert', path_input, "-gravity", "North", "-background", "white", "-fill", "black", "-splice", "0x90", "-pointsize", "28",  "-font", "Helvetica", "-annotate", "+0+45", label, path_output])

    #label = f" Dark Red=Avg 7-Day Deaths > 1 per 500,000  Bright Red=Avg 7-Day Deaths > 1 per 100,000 \n www.statmap/httpdocs.org"
    label = f"Pink=Avg 7-Day Deaths < 1 per 500,000    Dark Pink=Avg 7-Day Deaths > 1 per 500,000    Bright Red=Avg 7-Day Deaths > 1 per 100,000\n www.statmap/httpdocs.org"
    path_input = path_output
    path_output = PATH_TMP+'label3.png'
    call(['convert', path_input, "-gravity", "South", "-background", "white", "-fill", "black", "-splice", "0x90", "-pointsize", "14",  "-font", "Helvetica", "-annotate", "+0+45", label, path_output])

    path_input = path_output
    map_file = date_code + '.' + 'hotzone.png'
    path_output = PATH_MAPS + map_file
    call(['convert', '-flatten', '-resize', '1000x864!', path_input, path_output])
    print(f"Map Installed: {path_output}")

    return path_output





#
# Main
#
# Generate heatmap pngs from json configs
#

with open(PATH_ALL_COUNTIES,'r') as fd:
    config  = json.load(fd)
    counties = config['counties']

    for county in counties:
        code = county['code']
        pop = county['pop']
        CountyPopDict[code] = pop


file_name_list = os.listdir(PATH_STATS_ROOT)
file_name_list = [file_name for file_name in file_name_list if 'us' in file_name and 'sw' not in file_name]
file_name_list.sort()

current_file_name = file_name_list[-1]
prev_file_name = file_name_list[-2]

# CJM DEV
#file_name_list = file_name_list[-2:]

stat_json_file = prev_file_name.replace('us', 'world')
prev_date_code = stat_json_file.split('.')[1]
path_stat_json_file = PATH_STATS_ROOT + stat_json_file

with open(path_stat_json_file,'r') as fd_stats:
    config  = json.load(fd_stats)
    stats = config['stats'][0]
    prev_deaths = int(stats['deaths'])
    print(path_stat_json_file, prev_deaths)

ANIMS_PER_DAY = 5

day_count = 0
prev_deaths = 0

for current_file_name in file_name_list:
    print(current_file_name)
    stat_json_file = current_file_name.replace('us', 'world')
    date_code = stat_json_file.split('.')[1]
    path_stat_json_file = PATH_STATS_ROOT + stat_json_file
    print('PROCESSING', date_code, path_stat_json_file, day_count)

    with open(path_stat_json_file,'r') as fd_stats:
        config  = json.load(fd_stats)
        stats = config['stats'][0]
        deaths = int(stats['deaths'])
        inc_deaths = deaths - prev_deaths
        if inc_deaths < 0: inc_deaths = 0
        inc = inc_deaths / ANIMS_PER_DAY

    for frame_count in range(1, ANIMS_PER_DAY):
        if day_count == 0: break
        deaths = int(prev_deaths + (inc * frame_count))
        print('ANIM', prev_date_code, frame_count)
        path_last_map = genHeatMap(current_file_name, frame_count, prev_date_code, deaths)

    with open(path_stat_json_file,'r') as fd_stats:
        config  = json.load(fd_stats)
        stats = config['stats'][0]
        deaths = int(stats['deaths'])
        prev_deaths = deaths
        prev_date_code = date_code
        path_last_map = genHeatMap(current_file_name, 0, date_code, deaths)
        day_count += 1


print(path_last_map)

if path_last_map == None:
    print('Map already current: ', PATH_ACTIVE_MAP)
else:
    call(['cp', path_last_map, PATH_ACTIVE_MAP])
    print(f"Map Deployed: {path_last_map} {PATH_ACTIVE_MAP}")


#
# generate hotzone maps
#
current_file_name = file_name_list[-1]
prev_file_name = file_name_list[-2]

day_count = 0
prev_deaths = 0
day_count = 0

for current_file_name in file_name_list:

    day_count += 1
    if day_count < MIN_DAYS_OFFSET0301: continue
    if current_file_name != file_name_list[-1]: continue

    stat_json_file = current_file_name.replace('us', 'world')
    date_code = stat_json_file.split('.')[1]
    path_stat_json_file = PATH_STATS_ROOT + stat_json_file
    print('PROCESSING', date_code, path_stat_json_file, day_count)

    with open(path_stat_json_file,'r') as fd_stats:
        config  = json.load(fd_stats)
        stats = config['stats'][0]
        deaths = int(stats['deaths'])
        prev_deaths = deaths
        prev_date_code = date_code
        path_last_map = genHotZoneMap(current_file_name, 0, date_code, inc_deaths)
        print(path_last_map)
        day_count += 1

    #break
    call(['cp', path_last_map, PATH_ACTIVE_HOTZONEMAP])
    print(f"Map Deployed: {path_last_map} {PATH_ACTIVE_HOTZONEMAP}")

"""
if path_last_map == None:
    print('Map already current: ', PATH_ACTIVE_HOTZONEMAP)
else:
    call(['cp', path_last_map, PATH_ACTIVE_HOTZONEMAP])
    print(f"Map Deployed: {path_last_map} {PATH_ACTIVE_HOTZONEMAP}")
"""

#








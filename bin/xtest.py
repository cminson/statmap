#!/usr/bin/python
import os
from shutil import copyfile


PATH_STATS_ROOT= '/var/www/statmap/data/stats/'

#
stats_list = os.listdir(PATH_STATS_ROOT)
stats_list = [stat_name for stat_name in stats_list if 'stats.2' in stat_name and 'swp' not in stat_name]
stats_list.sort()
for stat in stats_list:
    out = stat.replace('stats', 'world')
    inputPath = PATH_STATS_ROOT + stat
    outputPath = PATH_STATS_ROOT + out
    print(inputPath, outputPath)
    copyfile(inputPath, outputPath)



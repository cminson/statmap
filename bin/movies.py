#!/usr/bin/python
import os
import shutil
from subprocess import call



PATH_MAPS = '/var/www/statmap/data/maps/'
PATH_MOVIES = '/var/www/statmap/data/movies/'

PATH_TMP = '/var/www/statmap/data/tmp/'
PATH_MOVIE_INPUTS = '/var/www/statmap/data/tmp/image%03d.png'
PATH_MOVIE_OUTPUT = '/var/www/statmap/data/movies/movie.mp4'
PATH_HOTZONES_MOVIE_INPUTS = '/var/www/statmap/data/tmp/hotzones%03d.png'
PATH_HOTZONES_MOVIE_OUTPUT = '/var/www/statmap/data/movies/hotzones.mp4'

#
# Main
#

print('Starting MP4 generation ...')

print('clearing: ', PATH_TMP)
shutil.rmtree(PATH_TMP)
os.mkdir(PATH_TMP)

print('generating spread map movie')
map_list = os.listdir(PATH_MAPS)
map_list = [map_name for map_name in map_list if '.heatmap' in map_name and 'swp' not in map_name]
map_list.sort()

index = 0
for map in map_list:

    index_string = "{:03d}".format(index)
    map_file = f"image{index_string}.png"
    path_output = PATH_TMP + map_file
    path_input = PATH_MAPS + map

    call(['cp', path_input, path_output])
    print(f"Movie Frame Installed: {path_input} {path_output}")

    index += 1

#
# generate movie mp4 into movies directory
#
print(f"Generating mp4:  {PATH_MOVIE_INPUTS} {PATH_MOVIE_OUTPUT}")
#call(['ffmpeg',"-r", "1/2", "-i", PATH_MOVIE_INPUTS, "-c:v", "libx264", "-vf", "fps=25,format=yuv420p", "-y", PATH_MOVIE_OUTPUT])
#call(['ffmpeg',"-r", "5", "-i", PATH_MOVIE_INPUTS, "-c:v", "libx264", "-vf", "fps=25,format=yuv420p", "-y", PATH_MOVIE_OUTPUT])
call(['ffmpeg',"-r", "15", "-i", PATH_MOVIE_INPUTS, "-c:v", "libx264", "-vf", "fps=25,format=yuv420p", "-y", PATH_MOVIE_OUTPUT])


print('generating hotzone  map movie')
map_list = os.listdir(PATH_MAPS)
map_list = [map_name for map_name in map_list if '.hotzone' in map_name and 'swp' not in map_name]
map_list.sort()

index = 0
for map in map_list:

    index_string = "{:03d}".format(index)
    map_file = f"hotzones{index_string}.png"
    path_output = PATH_TMP + map_file
    path_input = PATH_MAPS + map

    call(['cp', path_input, path_output])
    print(f"Movie Frame Installed: {path_input} {path_output}")

    index += 1

#
# generate movie mp4 into movies directory
#
print(f"Generating mp4:  {PATH_MOVIE_INPUTS} {PATH_MOVIE_OUTPUT}")
call(['ffmpeg',"-r", "2", "-i", PATH_HOTZONES_MOVIE_INPUTS, "-c:v", "libx264", "-vf", "fps=25,format=yuv420p", "-y", PATH_HOTZONES_MOVIE_OUTPUT])








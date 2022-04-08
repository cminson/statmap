#!/usr/bin/python3
import os
import sys
import json
from subprocess import call
from PIL import Image, ImageDraw, ImageFont



CANVAS_IMAGE_PATH = './base.png'
DEM_STATE_COLOR = (173,216,230)
GOP_STATE_COLOR = (255,0,0)
TEXT_COLOR = (0,0,0)
TITLE_COLOR = (0,0,0)

MAX_DISPLAY_STATES = 20

BAR_Y = 18
SLOT_Y = 22
SIZE_CHART_FONT = 12
SIZE_TITLE_FONT = 20
SIZE_DEATH_FONT = 20
CHART_OFFSET_X = 120
CHART_OFFSET_Y = 100
PIXELS_PER_UNIT = 5
FRAMES_PER_DAY = 20
MOVE_ANIMS_PER_DAY = 5

CANVAS_HEIGHT = 200 + MAX_DISPLAY_STATES * SLOT_Y
CANVAS_WIDTH = 1200
CHART_WIDTH = CANVAS_WIDTH - CHART_OFFSET_X

TEXT_TITLE = 'COVID-19: Top 20 States Ranked by Deaths Per 100,000 People'
TEXT_LABEL_X = 'Deaths Per 100,000'

CHART_FONT = ImageFont.truetype('../fonts/tahoma.ttf', size=SIZE_CHART_FONT)
TITLE_FONT = ImageFont.truetype('../fonts/tahoma.ttf', size=SIZE_TITLE_FONT)
DEATH_TITLE_FONT = ImageFont.truetype('../fonts/tahomabd.ttf', size=SIZE_DEATH_FONT)

PATH_IMAGES = '/var/www/statmap/httpdocs/data/images/'
PATH_MOVIE_INPUT = '/var/www/statmap/httpdocs/data/images/image%04d.png'
PATH_MOVIE_OUTPUT = '/var/www/statmap/httpdocs/data/movies/ranked20movie.mp4'

PATH_ALL_STATES = '/var/www/statmap/httpdocs/data/ALLSTATES.json'
PATH_STATS_ROOT= '/var/www/statmap/httpdocs/data/stats/'

MAX_CHART_HEIGHT = ((MAX_DISPLAY_STATES * SLOT_Y))

ALL_STATES = []
STATES_BY_POP = []

STATE_COLOR_DICT = {
'AK': GOP_STATE_COLOR, 'AL': GOP_STATE_COLOR, 'AR': GOP_STATE_COLOR,  'AZ': GOP_STATE_COLOR, 'CA': DEM_STATE_COLOR, 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi', 'MT': 'Montana', 'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': DEM_STATE_COLOR, 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}


def draw_state(y, code, ratio, canvas):


    if y > MAX_CHART_HEIGHT: return
    ratio = round(ratio, 2)

    draw = ImageDraw.Draw(canvas)
    color = (0, 0, 0)
    x = int(ratio * PIXELS_PER_UNIT)
    y = CHART_OFFSET_Y + y

    size = draw.textsize(code, font = CHART_FONT)
    x_font = CHART_OFFSET_X - size[0] - 4
    draw.text((x_font, y + 3), code, fill=TEXT_COLOR, font = CHART_FONT)

    coords = [(CHART_OFFSET_X, y), (x + CHART_OFFSET_X, y+BAR_Y)]
    #draw.rectangle(coords, fill = 'black')
    draw.rectangle(coords, fill = '#8B0000')

    ratio = "{:.2f}".format(ratio)
    draw.text((x + CHART_OFFSET_X + 5, y + 3), ratio, fill=TEXT_COLOR, font = CHART_FONT)
    del draw


def draw_chart():

    canvas = Image.new('RGB', (CANVAS_WIDTH,CANVAS_HEIGHT), color='white')
    draw = ImageDraw.Draw(canvas)

    text_len = draw.textsize(TEXT_TITLE, font = TITLE_FONT)[0]
    offset = (CANVAS_WIDTH / 2 ) - (text_len / 2)
    draw.text((offset, 10), TEXT_TITLE, fill=TITLE_COLOR, font = TITLE_FONT)

    end_y = CHART_OFFSET_Y + (MAX_DISPLAY_STATES * SLOT_Y) + SLOT_Y
    coords = [(CHART_OFFSET_X, CHART_OFFSET_Y), (CHART_OFFSET_X, end_y)]
    draw.line(coords, fill='black')
    coords = [(CHART_OFFSET_X, end_y), (CHART_WIDTH, end_y)]
    draw.line(coords, fill='black')

    text_len = draw.textsize(TEXT_LABEL_X, font = CHART_FONT)[0]
    offset = (CANVAS_WIDTH / 2 ) - (text_len / 2)
    draw.text((offset, end_y + 10), TEXT_LABEL_X, fill=TEXT_COLOR, font = CHART_FONT)
    return canvas

def update_death_count(canvas, usdate, deaths):

    draw = ImageDraw.Draw(canvas)
    text_len = draw.textsize("100000", font = DEATH_TITLE_FONT)[0]
    deaths = int(deaths)
    text_total_deaths = f'{usdate} {deaths:,} deaths'
    text_len = draw.textsize("100000", font = DEATH_TITLE_FONT)[0]
    text_len = draw.textsize(text_total_deaths, font = DEATH_TITLE_FONT)[0]
    offset = (CANVAS_WIDTH / 2 ) - (text_len / 2)
    draw.text((offset, 50), text_total_deaths, fill=TITLE_COLOR, font = DEATH_TITLE_FONT)



#
# main
#
len = len(sys.argv)
if len == 2:
    MAX_DISPLAY_STATES = 50
    CANVAS_HEIGHT = 200 + MAX_DISPLAY_STATES * SLOT_Y
    MAX_CHART_HEIGHT = ((MAX_DISPLAY_STATES * SLOT_Y))
    TEXT_TITLE = 'COVID-19: U.S. States Ranked by Deaths Per 100,000 People'
    PATH_MOVIE_OUTPUT = '/var/www/statmap/httpdocs/data/movies/ranked50movie.mp4'

    
print(f"Starting generation for {MAX_DISPLAY_STATES} ...")




#
# clear image directory
#
file_name_list = os.listdir(PATH_IMAGES)
for file_name in file_name_list:
    file_path = PATH_IMAGES + file_name
    print('Removing working images: ', file_path)
    os.remove(file_path)


#
# get all death numbers, keyed by date
# do this so as to report final death numbers which are consistent
# with other reports
#
DateToDeathsDict = {}
json_list = os.listdir(PATH_STATS_ROOT)
json_list = [json_name for json_name in json_list if 'world' in json_name and 'swp' not in json_name]
json_list.sort()
for json_name in json_list:
    date_code = json_name.split('.')[1]
    path_json = PATH_STATS_ROOT + json_name
    with open(path_json,'r') as fd:
        config  = json.load(fd)
        deaths = config['stats'][0]['deaths']
        DateToDeathsDict[date_code] = deaths


StatePopDict = {}
with open(PATH_ALL_STATES,'r') as fd:
    config  = json.load(fd)
    states = config['states']
    for state in states:
        code = state['code']
        pop = state['pop']
        name = state['name']

        ALL_STATES.append((pop, code, name))
        StatePopDict[code] = pop

ALL_STATES.sort()


day_count = 0
prev_total_deaths = 0
prev_ratio_dict = {}
prev_states = []

file_name_list = os.listdir(PATH_STATS_ROOT)
file_name_list = [file_name for file_name in file_name_list if 'top' in file_name and 'sw' not in file_name]
file_name_list.sort()

for file_name in file_name_list[50:]:
#for file_name in file_name_list:

    print('Processing: ', file_name)
    terms = file_name.split('.')[1]
    date_code = terms
    year = terms[0]+terms[1]
    month = terms[2]+terms[3]
    day = terms[4]+terms[5]
    usdate = f'{month}/{day}/{year}'
    path_state_file = PATH_STATS_ROOT + file_name

    with open(path_state_file,'r') as fd:

        config  = json.load(fd)
        states = config['top_state_deaths']
        states.pop()  # get rid of the last USA average entry
        total_deaths = 0
        for  state in states:
            deaths = state['deaths']
            total_deaths += int(deaths)
        inc_death = (total_deaths - prev_total_deaths) / FRAMES_PER_DAY

        #
        # compute incrementals for bar graphs
        #
        inc_ratio_dict = {}
        for slot, state in enumerate(states):
            if day_count == 0: break

            code = state['code']
            name = state['state_name']
            deaths = state['deaths']
            ratio = state['ratio']
            prev_ratio = prev_ratio_dict[code]
            diff = ratio - prev_ratio
            inc = diff / FRAMES_PER_DAY
            inc_ratio_dict[code] = inc

        #
        # compute incrementals for moving states to new rankings
        #
        prev_slot = 0
        inc_slot_dict = {}
        for prev_slot, _ in enumerate(prev_states):
            if day_count == 0: break

            prev_code = prev_states[prev_slot]['code']
            code = states[prev_slot]['code']
            for i, state in enumerate(states):
                if prev_code == state['code']: 
                    slot = i
                    break

            diff_slot = slot - prev_slot
            inc = (diff_slot * SLOT_Y) / FRAMES_PER_DAY
            inc_slot_dict[prev_code] =  inc

            #print(prev_code, code, prev_slot, slot)

        #
        # draw the animated frames
        #
        """
        for anim_frame_count in range(1, FRAMES_PER_DAY):
            if day_count == 0: break

            canvas = draw_chart()
            for prev_slot, prev_state in enumerate(prev_states):
                prev_code = prev_state['code']
                prev_name = prev_state['state_name']

                # animate the bar graph
                prev_ratio = prev_ratio_dict[prev_code]
                inc = inc_ratio_dict[prev_code] * anim_frame_count
                ratio = prev_ratio + inc

                # if any changes in rankings, animate the movement of rankings
                inc = 0
                if anim_frame_count < MOVE_ANIMS_PER_DAY:
                    if prev_code in inc_slot_dict:
                        inc = inc_slot_dict[prev_code] * anim_frame_count * (FRAMES_PER_DAY / MOVE_ANIMS_PER_DAY)

                draw_state(prev_slot * SLOT_Y + inc, prev_name, ratio, canvas)

            index_string = "{:04d}".format((day_count * FRAMES_PER_DAY) - FRAMES_PER_DAY + anim_frame_count )
            movie_frame = f"image{index_string}.png"
            path_output = PATH_IMAGES + movie_frame
            print('Interim Saving: ', path_output)
            update_death_count(canvas, prev_usdate, prev_total_deaths + (anim_frame_count * inc_death))
            canvas.save(path_output)
            #print(inc_slot_dict)
            #exit()
        """
        #
        # END for anim_frame_count in range(1, FRAMES_PER_DAY):
        #

        # draw the final day frame
        canvas = draw_chart()
        #for slot, state in enumerate(states[0:10]):
        total_deaths = 0 
        for slot, state in enumerate(states):
            code = state['code']
            name = state['state_name']
            deaths = state['deaths']
            ratio = state['ratio']
            prev_ratio_dict[code] = ratio
            #print(code, name, ratio, slot * SLOT_Y)

            draw_state(slot * SLOT_Y, name, ratio, canvas)
            state[code] = slot

            total_deaths += int(deaths)
            prev_total_deaths = total_deaths

        prev_usdate = usdate

        total_deaths = DateToDeathsDict[date_code]
        #print(date_code, total_deaths)
        update_death_count(canvas, usdate, total_deaths)
        #exit()

        prev_states = states
        frame = day_count * FRAMES_PER_DAY
        index_string = "{:04d}".format(frame)
        movie_frame = f"image{index_string}.png"
        path_output = PATH_IMAGES + movie_frame
        print('Saving: ', path_output)
        canvas.save(path_output)

    day_count += 1
            
call(['ffmpeg',"-r", "30", "-i", PATH_MOVIE_INPUT, "-c:v", "libx264", "-vf", "fps=10,format=yuv420p", "-y", PATH_MOVIE_OUTPUT])
            




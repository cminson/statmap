#!/usr/bin/python
import sys
import os
import json
import MySQLdb as mdb

#mysqldump -uroot covid19 > dump.sql

STATE_DICT = {
'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
}

DROP_TABLE = "drop table stats";
CREATE_TABLE = "create table stats (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, date_code varchar(8), day int, state varchar(32), county_name varchar(32), county_code varchar(6), total_cases int, new_cases int, total_deaths int, new_deaths int)"

try:
    con = mdb.connect('localhost', 'root', '', 'covid19');
    cur = con.cursor()

    cur.execute(DROP_TABLE)
    con.commit()

    cur.execute(CREATE_TABLE)
    con.commit()

except mdb.Error as e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(e)
    sys.exit(1)


PATH_STATS_ROOT= '/var/www/statmap/ndata/stats/'

file_name_list = os.listdir(PATH_STATS_ROOT)
file_name_list = [file_name for file_name in file_name_list if 'counties' in file_name and 'sw' not in file_name]
file_name_list.sort()

con = mdb.connect('localhost', 'root', '', 'covid19');
cur = con.cursor()
prev_day_dict = {}
day_index = 0
for file_name in file_name_list:

    path_county_file = PATH_STATS_ROOT + file_name
    with open(path_county_file,'r') as fd:
        config  = json.load(fd)
        date = config['usdate']
        (month, day, year) = date.split('/')
        date_code = f'{year}{month}{day}'
        counties = config['counties']

        #if date_code < '20200701': continue
        print(date_code)

        for county in counties:

            county_code = county['code'].replace('x','')

            prev_total_cases = prev_total_deaths = 0
            if county_code in prev_day_dict:
                prev_total_cases = prev_day_dict[county_code][0]
                prev_total_deaths = prev_day_dict[county_code][1]

            county_name = county['name']
            state_code = county['state'].replace(' ','')
            total_cases = county['cases']
            total_deaths = county['deaths']
            new_cases = total_cases - prev_total_cases
            new_deaths = total_deaths - prev_total_deaths
            prev_day_dict[county_code] = (total_cases, total_deaths)
            #print('dict', total_cases, total_deaths)

            query = f"insert into stats (date_code, day, state, county_name, county_code, total_cases, new_cases, total_deaths, new_deaths) values ('{date_code}', '{day_index}', '{state_code}', '{county_name}', '{county_code}', {total_cases}, {new_cases}, {total_deaths}, {new_deaths})"
            #print(query)
            cur.execute(query)
            con.commit()

    for state_code in STATE_DICT.keys():

        query = f"select sum(total_cases), sum(new_cases), sum(total_deaths), sum(new_deaths)  from stats where state='{state_code}' and county_name!='{state_code}' and day='{day_index}'"
        #print(query)
        cur.execute(query)
        row = cur.fetchall()[0]
        total_cases = row[0]
        new_cases = row[1]
        total_deaths = row[2]
        new_deaths = row[3]
  
        county_name = 'State Totals'
        county_code = '0'
        query = f"insert into stats (date_code, day, state, county_name, county_code, total_cases, new_cases, total_deaths, new_deaths) values ('{date_code}', '{day_index}', '{state_code}', '{county_name}', '{county_code}', {total_cases}, {new_cases}, {total_deaths}, {new_deaths})"
        #print(query)
        cur.execute(query)


    day_index += 1 




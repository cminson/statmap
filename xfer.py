#!/usr/bin/python
import json
import datetime

print("{")
print("\"counties\": [")
code = "c33433"
state = "CA"
name = "Alameda"

count = 0
with open('./data/svg/save', 'r') as fd:

    lines = fd.readlines()
    for line in lines:
        #print(line, end="")

        if (count % 2) == 0:
            #print(line)
            tmp = line.split("\"")
            code = tmp[1]
            #code = "\"" + code + "\""
            #print(code)
            count += 1
            continue

    
        tmp = line.split(">")
        #print(tmp)
        if len(tmp) < 2:
            #print(tmp)
            exit(0)
        tmp = tmp[1]
        #tmp = tmp.replace("<\/title", "")
        tmp = tmp.replace("title", "")
        tmp = tmp.replace("<", "")
        tmp = tmp.replace("/", "")
        tmp = tmp.split(",")
        name = tmp[0]
        state = tmp[1]
        s = (f"[\"code\": \"{code}\", \"state\": \"{state}\", \"name\": \"{name}\"],")
        s = s.replace('[', '{');
        s = s.replace(']', '}');
        print(s)
        count += 1

print("]")
print("}")


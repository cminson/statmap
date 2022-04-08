#!/usr/local/bin/julia

using JSON
using Dates


PATH_STATS_ROOT= "/var/www/statmap/data/stats/"

daily_list = readdir(PATH_STATS_ROOT)
daily_list = sort(daily_list)

PrevDeaths = 0
DaysOfWeek = Dict([(1, "Mon"), (2, "Tue"), (3, "Wed"), (4, "Thu"), (5, "Fri"), (6, "Sat"), (7, "Sun")])

function test()
    println("hello Dict")
end
function test1(x::Int)
    println("hello Int")
end
function test1(x::Float64)
    println("hello Float")
end
TestDict = Dict([("TEST", test)])

for (i,world_file) in enumerate(daily_list)
    global PrevDeaths
    total_deaths = inc_deaths = 0

    occursin(".swp", world_file) && continue
    occursin("world", world_file) || continue
    path_world_file = PATH_STATS_ROOT * world_file

    open(path_world_file, "r") do f
        data = read(f, String)
        config = JSON.parse(data)
        stats = config["stats"]
        total_deaths = stats[1]["deaths"]
        inc_deaths = total_deaths - PrevDeaths
        PrevDeaths = total_deaths
    end

    d = replace(world_file, "world." => "")
    d = replace(d, ".json" => "")
    year = parse(Int, (SubString(d, 1, 2)))
    month = parse(Int, SubString(d, 3, 4))
    day = parse(Int, SubString(d, 5, 6))
    #date = Dates.Date(2020, 5, 12)
    date = Dates.Date(year, month, day)
    dayName =  DaysOfWeek[Dates.dayofweek(date)]
    println(date, " ", dayName, " ", total_deaths, " ", inc_deaths)
end
x = 1 in keys(DaysOfWeek)
println(x)
test1(3)
test1(3.0)
if "TEST" in keys(TestDict)
    TestDict["TEST"]()
end


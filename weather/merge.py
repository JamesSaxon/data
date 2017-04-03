#!/usr/bin/env python 

import pandas as pd
import pytz
import os  

def merge_weather_data(airport, tz):

    df_list = []
    for y in range(2000, 2017):
        for m in range(1, 13):
            for d in range(1, 32):
                
                f = "{}/{:04d}{:02d}{:02d}".format(airport, y, m, d)
                if not os.path.isfile(f): continue
                
                print(f)
                df_list.append(pd.read_csv(f, index_col = "DateUTC", parse_dates = ['DateUTC']))
                
    df = pd.concat(df_list)
    
    # Drop a few bogus values
    df = df[df['TemperatureF'] != -9999.0]
    df["PrecipitationIn"].fillna(0, inplace = True)
    
    df.set_index(df.index.tz_localize(pytz.UTC).tz_convert(pytz.timezone('US/' + tz)),
                 inplace = True)
    
    df.rename(columns = {"TemperatureF" : "Temperature [F]", "PrecipitationIn" : "Precipitation [In]"})\
      .to_csv(airport + ".csv")


airports = [["PDX", "Pacific"], ["JFK", "Eastern"], ["PHL", "Eastern"], 
            ["LAX", "Pacific"], ["BOS", "Eastern"], ["PHX", "Mountain"], 
            ["DEN", "Mountain"], ["SFO", "Pacific"], ["DFW", "Central"],
            ["MCO", "Eastern"]]

for a, tz in airports:
    merge_weather_data(a, tz)


# -*- coding: utf-8 -*-
"""
Created on Mon May  8 12:29:26 2023

@author: ack98
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May  6 09:47:37 2023

@author: ack98
"""

#grab the data from aviationweather.gov.  Index to the comment right before the data 
#make sure to grab the airports between code tags 
import requests as rq
import re
from collections import OrderedDict
from operator import getitem
from operator import itemgetter
# Separate multiple airports by commas
def get_data(link):
    lnk = "https://aviationweather.gov/metar/data?ids=KTYS,KBNA,KVGT,KLAS&format=raw&date=&hours=0" 
    data = rq.get(lnk) 
    needle = "<!-- Data starts here -->" 
    needle_position = data.text.find(needle) + len(needle) 
    data = data.text[needle_position:] 
    needle = "<!-- Data ends here -->" 
    needle_position = data.find(needle) 
    data = data[:needle_position]

    metars = []
    needle = "<code>"
    while True: 
        pos_s = data.find(needle) 
        if pos_s == -1: 
            break 
        pos_e = data.find("</code>") 
        if pos_e != -1: 
            apt = data[pos_s + len(needle):pos_e] 
            data = data[pos_e + len(needle) + 1:] 
        else: 
            apt = data[pos_s + len(needle):] 
            data = ""
        metars.append(apt) 
        
    return metars

    


def make_dict(metars):
    data_dict = {}
    for i in metars:
        data = i.split(" ")
        #print(data)
        airport =data[0]
        data_dict[airport] = {}
        data_dict[airport] = dict.fromkeys(['date','UTC','wind_dir','wind_speed',
                                            'vis','degrees', 'dewpoint','altimeter'],[])
    
        for d in data:
            #print(d)
            timestr = "Z"
            windstr = "KT"
            guststr = "G"
            visstr = "SM"
            degdewstr = "/"
            altstr = "A"
            if timestr in d: 
                #print(d)
                #get the date
                date = d[0:2]
                data_dict[airport]['date'] = date
            
                #get the utc
                utc = d[2:6]
                data_dict[airport]['UTC'] = utc 
                
            #get wind direction, wind gust and wind speed 
            elif windstr in d:
                #print(d)
                wind_dir = d[0:3]
                data_dict[airport]["wind_dir"] = wind_dir
                
                if guststr in d:
                    gust = d[d.find(guststr) + len(guststr):d.rfind(windstr)]
                    data_dict[airport]["wind_gust"] = gust 
                    #print(gust)
                    #now get windspeed which is 2 characters before G 
                    #windspd =  d.split(guststr)
                    gindex = d.index("G")
                    spdindex1 = gindex -2
                    wind_speed = d[spdindex1:gindex]
                    data_dict[airport]["wind_speed"] = wind_speed
                else: 
                    data_dict[airport]["wind_gust"] = 0
                    winindex = d.index(windstr)
                    spdindex1 = winindex -2
                    wind_speed = d[spdindex1:winindex]
                    data_dict[airport]["wind_speed"] = wind_speed
            
            #get visibility 
            elif visstr in d:
                nums = ""
                for c in d:
                    if c.isdigit():
                        nums = nums + c 
                data_dict[airport]["vis"] = nums
            
            
            elif degdewstr in d:
                neg = "M"
                splt = d.split("/")
                temp = splt[0]
                if neg in temp:
                    negtemp = temp.replace(neg,"-")
                    data_dict[airport]["degrees"] = negtemp
                    #print(negtemp)
                else:
                    data_dict[airport]["degrees"] = temp
                dew = splt[1]
                if neg in dew:
                    negdew = dew.replace(neg, "-")
                    data_dict[airport]["dewpoint"] = negdew
                else:
                    data_dict[airport]["dewpoint"] = dew
            
            elif altstr in d:
                if len(d) == 5:
                    altimeter = d.strip(altstr)
                    altlist = list(altimeter)
                    altlist.insert(2,".")
                    newalt = "".join(altlist)
                    data_dict[airport]["altimeter"] = newalt
                else:
                    continue
            else:
                continue
    return data_dict 

        

#now get everything plotting 

import tkinter as tk
from tkinter import *

def run(data_dict):
        result = [[k, v] for k,v in data_dict.items()]
        #print(result)
        res = list(map(itemgetter(1), result))
        #final = list(map(itemgetter('wind_gust'),res))
        # Create the root Tk()
        win1 = tk.Tk()
        # Set the title
        win1.title("test")
        # Create two frames, the list is on top of the Canvas
        list_frame = tk.Frame(win1)
        draw_frame = tk.Frame(win1)
        # Set the list grid in c,r = 0,0
        list_frame.grid(column=0, row=0)
        # Set the draw grid in c,r = 0,1
        draw_frame.grid(column=0,row=1)

        # Create the canvas on the draw frame, set the width to 800 and height to 600
        canvas = tk.Canvas(draw_frame, width=800, height=600)
        # Reset the size of the grid
        canvas.pack()

        # THESE ARE EXAMPLES! You need to populate this list with the available airports in the METAR 
        # which is given by metar parameter passed into this function.
        #get list of available airport 
        air_list = []
        for airport in data_dict:
            air_list.append(airport)
        choices = air_list

        # Create a variable that will store the currently selected choice.
        airvar = tk.StringVar(win1)
        # Immediately set the choice to the first element. Double check to make sure choices[0] is valid!
        airvar.set(choices[0])
        
        #get date data to match airvar 
        #print(result)
        time_vals = list(map(itemgetter('UTC'),res))
        time_list =[]
        for i in time_vals:
            time_list.append(i)
        time_options = time_list
        #create variable to store date data 
        timevar = tk.StringVar(win1)
        timevar.set(time_options[0])
            
        
        
        # Create the dropdown menu with the given choices and the update variable. This is stored on the
        # list frame. You must make sure that choices is already fully populated.
        dropdown = tk.OptionMenu(list_frame, airvar, *choices)
        # The dropdown menu is on the top of the screen. This will make sure it is in the middle.
        dropdown.grid(row=0,column=1)
        # This function is called whenever the user selects another. Change this as you see fit.
        def drop_changed(*args):
                canvas.delete("airport_text")
                canvas.create_text(100, 100, text = airvar.get(), fill="red", tags="airport_text")
                canvas.delete("time_text")
                canvas.create_text(100, 115, text = timevar.get(), fill="blue", tags="time_text")
        # Listen for the dropdown to change. When it does, the function drop_changed is called.
        airvar.trace('w', drop_changed)
        # You need to draw the text manually with the first choice.
        #vals = data_dict[(list(data_dict.keys())[0])]
        #time = data_dict['date']
        #canvas.create_text(100, 115, text = time, fill="blue", tags="test")
        
        
        
        drop_changed()
        # mainloop() is necessary for handling events
        tk.mainloop()
        
if __name__ == "__main__":
        data = rq.get("https://aviationweather.gov/metar/data?ids=KTYS&format=raw&date=&hours=0")
        metars = get_data(data)
        get_dict = make_dict(metars)
        run(get_dict)

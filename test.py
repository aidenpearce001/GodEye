import requests
import json 
import re, os, time
from random import choice
import urllib.parse

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import folium

chars = "abcdefghijklmnopqrstuvwxyz0123456789"

xdc = "_xdc_._" + "".join([y for x in range(6) if (y := choice(chars)) is not None])

# Effiel Tower Coordinate 
lat = 48.8583701
lng = 2.2944813

radius = 500

map_center = [lat, lng]
map_zoom = 15
map = folium.Map(location=map_center, zoom_start=map_zoom)

# Add a marker to the map
marker = folium.Marker(location=map_center, tooltip='My Location')
marker.add_to(map)

# Save the map as an HTML file

delay=5
fn='map.html'
tmpurl='file://{path}/{mapfile}'.format(path=os.getcwd(),mapfile=fn)
map.save(fn)

options = Options()
options.headless = True
  
# initializing webdriver for Chrome with our options
browser = webdriver.Firefox(options=options)

browser.get(tmpurl)

delay=5
#Give the map tiles some time to load
time.sleep(delay)

browser.save_screenshot('map.png')
browser.quit()294206

# Travel Path Coordinate
# 48.856975, 2.293986
# 48.857018, 2.294056
# 48.85706, 2.294109
# 48.857099, 2.294168
# 48.85712, 2.294206
# 48.857138, 2.294233
# 48.857173, 2.294276
# 48.857208, 2.294329
# 48.857251, 2.294399
# 48.8573, 2.294458
# 48.857332, 2.294517
# 48.857385, 2.294587
# 48.85742, 2.294641
# 48.857452, 2.294689
# 48.857505, 2.294769
# 48.857554, 2.294834
# 48.8576, 2.294909
# 48.857649, 2.294978
# 48.857681, 2.295038

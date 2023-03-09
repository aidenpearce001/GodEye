import requests
import json 
import re, os, time
from random import choice
import urllib.parse

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import folium

import streetview

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
browser.quit()

# def download_pano(panoid, filename, zoom=3):
#     panorama = streetview.download_panorama_v3(panoid, zoom=zoom, disp=False, filename=filename, alternate=False)
#     if panorama: # Worked downloading
#         pass
#     else:
#         panorama = streetview.download_panorama_v3(panoid, zoom=zoom, disp=False, filename=filename, alternate=True)
#         if not panorama:
#             raise(ValueError('Could not fetch Panorama with the given ID'))
#         fix_cropping(filename)

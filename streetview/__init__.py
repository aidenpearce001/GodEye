# -*- coding: utf-8 -*-
"""
:Module: ``streetview``
:Author: `Adrian Letchford <http://www.dradrian.com>`_
:Organisation: `Warwick Business School <http://www.wbs.ac.uk/>`_, `University of Warwick <http://www.warwick.ac.uk/>`_.


This is a light module for downloading photos from Google street view. The
functions allow you to retrieve current and **old** photos.

The photos on Google street view are panoramas and are refered to as such.
However, you have the option of downloading flat photos, or panoramas.

Retrieving photos is a two step process. First, you must translate GPS
coordinates into panorama ids. The following code retrieves a list of
the closest panoramas giving you their id and date:

>>> import streetview
>>> panoids = streetview.panoids(lat, lon)

You can then use the panorama ids to download photos with the following
function:

>>> streetview.api_download(panoid, heading, flat_dir, key)

"""

import re, math
from datetime import datetime
import requests
import time
import shutil
import itertools
from PIL import Image
from io import BytesIO
import os
from random import choice

from pprint import pprint

imgx = 26 # Modified image width. Default is 26 which sometimes results in crop.

class urls:
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    def _build_tile_url(pano_id, zoom=3, x=0, y=0):
        """
        Build Google Street View Tile URL
        """
        url = f"https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={pano_id}&x={x}&y={y}&zoom={zoom}&nbt=1&fover=2"
        return url

    def _build_metadata_url(pano_id=None, lat=None, lng=None, mode="GetMetadata", radius=500):
        """
        Build GeoPhotoService call URL from
        Pano ID that contains panorama key data 
        such as image size, location, coordinates,
        date and previous panoramas.
        """
        xdc = "_xdc_._" + "".join([y for x in range(6) if (y := choice(urls.chars)) is not None])

        print(xdc)
        
        if mode == "GetMetadata":
            url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.GetMetadata?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m2!1sen!2sUS!3m3!1m2!1e2!2s{pano_id}!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}"
        elif mode == "SingleImageSearch":
            url = f"https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{lat}!4d{lng}!2d{radius}!3m20!1m1!3b1!2m2!1sen!2sUS!9m1!1e2!11m12!1m3!1e2!2b1!3e2!1m3!1e3!2b1!3e2!1m3!1e10!2b1!3e2!4m6!1e1!1e2!1e3!1e4!1e8!1e6&callback={xdc}"
        elif mode == "SatelliteZoom":
            x, y = geo._coordinate_to_tile(lat, lng)
            url = f"https://www.google.com/maps/photometa/ac/v1?pb=!1m1!1smaps_sv.tactile!6m3!1i{x}!2i{y}!3i17!8b1"

        return url

    def _build_short_url(pano_id, heading=0, pitch=0, zoom=90) -> str:
        """
        Build API call URL that shorts an encoded URL.
        Useful for shortening panorama IDs.
        """
        encoded_input = f"https://www.google.com/maps/@?api=1&map_action=pano&pano={pano_id}&heading={heading}&pitch={pitch}&fov={zoom}"
        url = f"https://www.google.com/maps/rpc/shorturl?pb=!1s{urllib.parse.quote(encoded_input)}"
        return url

class geo:
    def _project(lat, lng, TILE_SIZE=256):
        siny = math.sin((lat * math.pi) / 180)
        siny = min(max(siny, -0.9999), 0.9999)
        x = TILE_SIZE * (0.5 + lng / 360),
        y = TILE_SIZE * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)),
        return x[0], y[0]
    def _coordinate_to_tile(lat, lng, tile_size=256, zoom=17):
        x, y = geo._project(lat, lng)
        zoom = 1 << zoom
        tile_x = math.floor((x * zoom) / tile_size)
        tile_y = math.floor((y * zoom) / tile_size)
        return tile_x, tile_y

def _panoids_url(lat, lon):

    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = ("https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?"
           "pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e2!6m1!1e2"
           "&callback=_xdc_._v2mub5")
    
    return url.format(lat, lon)


def _panoids_data(lat, lon, proxies=None):
    """
    Gets the response of the script on Google's servers that returns the
    closest panoramas (ids) to a give GPS coordinate.
    """
    url = _panoids_url(lat, lon)
    return requests.get(url, proxies=None)


def panoids(lat, lon, closest=False, disp=False, proxies=None, resp=None):
    """
    Gets the closest panoramas (ids) to the GPS coordinates.
    If the 'closest' boolean parameter is set to true, only the closest panorama
    will be gotten (at all the available dates)
    """
    resp = _panoids_data(lat, lon)

    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    # 2015
    # XXXX
    # XXXX
    # 2012
    # 2013
    # 2014
    pans = re.findall('\[2,"(.+?)"\].+?'
                      '\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)\],'
                      '\[-?[0-9]+.[0-9]+\],\[(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', resp.text)
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2]),
        "heading": float(p[3]),
        "tilt": float(p[4]),
        "roll": float(p[5])} for p in pans]  # Convert to floats

    # Remove duplicate panoramas
    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    if disp:
        for pan in pans:
            print(pan)

    # Get all the dates
    # The dates seem to be at the end of the file. They have a strange format but
    # are in the same order as the panoids except that the latest date is last
    # instead of first.
    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', resp.text)
    dates = [list(d)[1:] for d in dates]  # Convert to lists and drop the index

    if len(dates) > 0:
        # Convert all values to integers
        dates = [[int(v) for v in d] for d in dates]

        # Make sure the month value is between 1-12
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]

        # The last date belongs to the first panorama
        year, month = dates.pop(-1)
        pans[0].update({'year': year, "month": month})

        # The dates then apply in reverse order to the bottom panoramas
        dates.reverse()
        for i, (year, month) in enumerate(dates):
            pans[-1-i].update({'year': year, "month": month})

    # # Make the first value of the dates the index
    # if len(dates) > 0 and dates[-1][0] == '':
    #     dates[-1][0] = '0'
    # dates = [[int(v) for v in d] for d in dates]  # Convert all values to integers
    #
    # # Merge the dates into the panorama dictionaries
    # for i, year, month in dates:
    #     pans[i].update({'year': year, "month": month})

    # Sort the pans array
    def func(x):
        if 'year'in x:
            return datetime(year=x['year'], month=x['month'], day=1)
        else:
            return datetime(year=3000, month=1, day=1)
        
    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans

def panoids_from_response(text, closest=False, disp=False, proxies=None):
    """
    Gets panoids from response (gotting asynchronously)
    """

    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    # 2015
    # XXXX
    # XXXX
    # 2012
    # 2013
    # 2014
    pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', text)
    pans = [{
        "panoid": p[0],
        "lat": float(p[1]),
        "lon": float(p[2])} for p in pans]  # Convert to floats

    # Remove duplicate panoramas
    pans = [p for i, p in enumerate(pans) if p not in pans[:i]]

    if disp:
        for pan in pans:
            print(pan)

    # Get all the dates
    # The dates seem to be at the end of the file. They have a strange format but
    # are in the same order as the panoids except that the latest date is last
    # instead of first.
    dates = re.findall('([0-9]?[0-9]?[0-9])?,?\[(20[0-9][0-9]),([0-9]+)\]', text)
    dates = [list(d)[1:] for d in dates]  # Convert to lists and drop the index

    if len(dates) > 0:
        # Convert all values to integers
        dates = [[int(v) for v in d] for d in dates]

        # Make sure the month value is between 1-12
        dates = [d for d in dates if d[1] <= 12 and d[1] >= 1]

        # The last date belongs to the first panorama
        year, month = dates.pop(-1)
        pans[0].update({'year': year, "month": month})

        # The dates then apply in reverse order to the bottom panoramas
        dates.reverse()
        for i, (year, month) in enumerate(dates):
            pans[-1-i].update({'year': year, "month": month})

    # # Make the first value of the dates the index
    # if len(dates) > 0 and dates[-1][0] == '':
    #     dates[-1][0] = '0'
    # dates = [[int(v) for v in d] for d in dates]  # Convert all values to integers
    #
    # # Merge the dates into the panorama dictionaries
    # for i, year, month in dates:
    #     pans[i].update({'year': year, "month": month})

    # Sort the pans array
    def func(x):
        if 'year'in x:
            return datetime(year=x['year'], month=x['month'], day=1)
        else:
            return datetime(year=3000, month=1, day=1)
    pans.sort(key=func)

    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans

def tiles_info(panoid, zoom=5, alternate=False):
    """
    Generate a list of a panorama's tiles and their position.

    The format is (x, y, filename, fileurl)
    """

    image_url = 'https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={}&zoom={}&x={}&y={}'

    # The tiles positions
    coord = list(itertools.product(range(imgx), range(13)))

    if alternate:
        image_url = 'https://lh3.ggpht.com/p/{}=x{}-y{}-z{}'
        tiles = [(x, y, "%s_%dx%d.jpg" % (panoid, x, y), image_url.format(panoid, x, y, zoom)) for x, y in coord]
    else:
        image_url = 'https://streetviewpixels-pa.googleapis.com/v1/tile?cb_client=maps_sv.tactile&panoid={}&zoom={}&x={}&y={}'
        tiles = [(x, y, "%s_%dx%d.jpg" % (panoid, x, y), image_url.format(panoid, zoom, x, y)) for x, y in coord]
    return tiles


def download_tiles(tiles, directory, disp=False):
    """
    Downloads all the tiles in a Google Stree View panorama into a directory.

    Params:
        tiles - the list of tiles. This is generated by tiles_info(panoid).
        directory - the directory to dump the tiles to.
    """

    for i, (x, y, fname, url) in enumerate(tiles):

        if disp and i % 20 == 0:
            print("Image %d (%d)" % (i, len(tiles)))

        # Try to download the image file
        while True:
            try:
                response = requests.get(url, stream=True)
                break
            except requests.ConnectionError:
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)

        with open(directory + '/' + fname, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


def stich_tiles(panoid, tiles, directory, final_directory, point=None):
    """
    Stiches all the tiles of a panorama together. The tiles are located in
    `directory'.
    """

    tile_width = 512
    tile_height = 512

    panorama = Image.new('RGB', (imgx*tile_width, 13*tile_height))

    for x, y, fname, url in tiles:

        fname = directory + "/" + fname
        tile = Image.open(fname)

        panorama.paste(im=tile, box=(x*tile_width, y*tile_height))

        del tile


    if point == None:
        name = f"{panoid}.jpg"
    else:
         name = f"{point[0]}_{point[1]}_{panoid}.jpg"

    panorama.save(os.path.join(final_directory, name), quality=30)


    del panorama


def delete_tiles(tiles, directory):
    for x, y, fname, url in tiles:
        os.remove(directory + "/" + fname)


def api_download(panoid, heading, flat_dir, key, width=640, height=640,
                 fov=120, pitch=0, extension='jpg', year=2017, fname=None):
    """
    Download an image using the official API. These are not panoramas.

    Params:
        :panoid: the panorama id
        :heading: the heading of the photo. Each photo is taken with a 360
            camera. You need to specify a direction in degrees as the photo
            will only cover a partial region of the panorama. The recommended
            headings to use are 0, 90, 180, or 270.
        :flat_dir: the direction to save the image to.
        :key: your API key.
        :width: downloaded image width (max 640 for non-premium downloads).
        :height: downloaded image height (max 640 for non-premium downloads).
        :fov: image field-of-view.
        :image_format: desired image format.
        :fname: file name

    You can find instructions to obtain an API key here: https://developers.google.com/maps/documentation/streetview/
    """
    if not fname:
        fname = "%s_%s_%s" % (year, panoid, str(heading))
    image_format = extension if extension != 'jpg' else 'jpeg'

    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        # maximum permitted size for free calls
        "size": "%dx%d" % (width, height),
        "fov": fov,
        "pitch": pitch,
        "heading": heading,
        "pano": panoid,
        "key": key
    }

    response = requests.get(url, params=params, stream=True)
    try:
        img = Image.open(BytesIO(response.content))
        filename = '%s/%s.%s' % (flat_dir, fname, extension)
        img.save(filename, image_format)
    except:
        print("Image not found")
        filename = None
    del response
    return filename


def download_flats(panoid, flat_dir, key, width=400, height=300,
                   fov=120, pitch=0, extension='jpg', year=2017):
    for heading in [0, 90, 180, 270]:
        api_download(panoid, heading, flat_dir, key, width, height, fov, pitch, extension, year)

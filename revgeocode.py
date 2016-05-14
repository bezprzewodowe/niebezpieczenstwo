#!/usr/bin/env python
# -*- coding: utf-8 -*-

# WiGLE.net + Google Maps

# (C) 2016 Adam Ziaja <adam@adamziaja.com> http://adamziaja.com

login = '?' # https://wigle.net
password = '?' # https://wigle.net
googlemaps_api_key = '?' # https://developers.google.com/maps/documentation/geolocation/get-api-key

import requests
#import requests.packages.urllib3
#requests.packages.urllib3.disable_warnings()
import json
import googlemaps # sudo pip install -U googlemaps
import sys

if len(sys.argv) == 2:
    ssid = sys.argv[1]
    gmaps = googlemaps.Client(key=googlemaps_api_key)

    s = requests.Session()
    api = 'https://wigle.net/api/v1/'
    s.post(api + 'jsonLogin', data = {'credential_0':login, 'credential_1':password, 'noexpire':'on', 'destination':''}) # wyszukiwanie dostępne tylko po zalogowaniu
    r = s.post(api + 'jsonSearch', data = {'latrange1':'', 'latrange2':'', 'longrange1':'', 'longrange2':'', 'variance':'0.010', 'netid':'', 'ssid':ssid, 'lastupdt':'', 'addresscode':'', 'statecode':'', 'zipcode':'', 'Query':'Query'})

    json_object = json.loads(r.text)
    for result in json_object['results']:
        if result['ssid'] == ssid: # ta sama wielkośc znaków, ponieważ zapytanie do WiGLE ignoruje, a proby WiFi mają wielkość jaka nas interesuje
            reverse_geocode_result = gmaps.reverse_geocode((result['trilat'], result['trilong']))
            print 'https://www.google.pl/maps?q=' + result['trilat'] + ',' + result['trilong'] + ' - ' + reverse_geocode_result[0]['formatted_address']
else:
    print('proszę podać w drugim argumencie nazwę sieci WiFi (SSID)')

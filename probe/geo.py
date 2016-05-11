#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) 2016 Adam Ziaja <adam@adamziaja.com> http://adamziaja.com

login = '?' # https://wigle.net
password = '?' # https://wigle.net
googlemaps_api_key = '?' # https://developers.google.com/maps/documentation/geolocation/get-api-key

import requests
# import requests.packages.urllib3
# requests.packages.urllib3.disable_warnings()
import json
import googlemaps
gmaps = googlemaps.Client(key=googlemaps_api_key)
import oursql

conn = oursql.connect(host='localhost', user='tapt', passwd='toor',
                      db='tapt', port=3307)
curs = conn.cursor(oursql.DictCursor)
curs.execute('CREATE TABLE IF NOT EXISTS geo (ID int NOT NULL AUTO_INCREMENT UNIQUE, ssid varchar(255) NOT NULL, gps varchar(255) NOT NULL, address varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci, PRIMARY KEY (ID), UNIQUE KEY `geo` (`ssid`, `gps`, `address`))'
             )

s = requests.Session()
api = 'https://wigle.net/api/v1/'
s.post(api + 'jsonLogin', data={
    'credential_0': login,
    'credential_1': password,
    'noexpire': 'on',
    'destination': '',
    }) # wyszukiwanie dostępne tylko po zalogowaniu

curs.execute('SELECT DISTINCT(ssid) FROM `probe`')
for ssid in curs:
    ssid = ssid['ssid']
    r = s.post(api + 'jsonSearch', data={
        'latrange1': '',
        'latrange2': '',
        'longrange1': '',
        'longrange2': '',
        'variance': '0.010',
        'netid': '',
        'ssid': ssid,
        'lastupdt': '',
        'addresscode': '',
        'statecode': '',
        'zipcode': '',
        'Query': 'Query',
        })

    json_object = json.loads(r.text)
    for result in json_object['results']:
        if result['ssid'] == ssid: # ta sama wielkośc znaków, ponieważ zapytanie do WiGLE ignoruje, a proby WiFi mają wielkość jaka nas interesuje
            try:
                reverse_geocode_result = \
                    gmaps.reverse_geocode((result['trilat'],
                        result['trilong']))
                gps = result['trilat'] + ',' + result['trilong']
                address = reverse_geocode_result[0]['formatted_address']
                address_components = \
                    reverse_geocode_result[0]['address_components']
            except IndexError:
                pass

            # curs.execute('INSERT IGNORE INTO `geo` (ssid, gps, address) VALUES (?, ?, ?)',(ssid, gps, address))
            for component in address_components:
                if any('country' in s for s in component['types']):
                    country = str(component['short_name'])
                    if country == 'PL':
                        try:
                            print ssid, reverse_geocode_result[0]['formatted_address']
                            curs.execute('INSERT IGNORE INTO `geo` (ssid, gps, address) VALUES (?, ?, ?)'
                                    , (ssid, gps, address))
                        except IndexError:
                            pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# WiGLE.net

# (C) 2016 Adam Ziaja <adam@adamziaja.com> http://adamziaja.com

import sys
import requests
import json

login = '?' # https://wigle.net
password = '?' # https://wigle.net

if len(sys.argv) == 2:
    ssid = sys.argv[1]
    s = requests.Session()
    api = 'https://wigle.net/api/v1/'
    s.post(api + 'jsonLogin', data = {'credential_0':login, 'credential_1':password, 'noexpire':'on', 'destination':''})
    r = s.post(api + 'jsonSearch', data = {'latrange1':'', 'latrange2':'', 'longrange1':'', 'longrange2':'', 'variance':'0.010', 'netid':'', 'ssid':ssid, 'lastupdt':'', 'addresscode':'', 'statecode':'', 'zipcode':'', 'Query':'Query'})

    json_object = json.loads(r.text)
    for result in json_object['results']:
        if result['ssid'] == ssid:
            print 'https://www.google.pl/maps?q=' + result['trilat'] + ',' + result['trilong']
else:
    print('proszę podać w drugim argumencie nazwę sieci WiFi (SSID)')

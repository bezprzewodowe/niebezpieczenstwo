#!/usr/bin/env python2

# Written by Maciej Grela <enki@fsck.pl>, wigle.net and googlemaps query code from Adam Ziaja <adam@adamziaja.com>

from __future__ import print_function

import sqlite3, json, sys, os, requests.packages.urllib3, time, re
requests.packages.urllib3.disable_warnings()

import googlemaps # sudo pip install -U googlemaps

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Default config
database_filename = 'essid_locations.sqlite'

login = os.environ['WIGLE_USERNAME'] # https://wigle.net
password = os.environ['WIGLE_PASSWORD']
googlemaps_api_key = os.environ['GOOGLEMAPS_API_KEY'] # https://developers.google.com/maps/documentation/geolocation/get-api-key

def add_ssid_results(results):

    # Gather stats on trilats and trilongs to check if SSID coverage is not too big
    trilats = []
    trilongs = []
    for result in results:
        eprint("essid='%s' result: %s" % (ssid,result))

        # Normalize some of the data
        result['netid'] = result['netid'].lower()
        result['trilat'] = float(result['trilat'])
        result['trilong'] = float(result['trilong'])

        if result['trilat'] == 0 and result['trilong'] == 0:
            eprint("essid='%s' Something is wrong with the coordinates, skipping result %s" % (ssid, result))
            continue

        # Calculate stats and skip SSIDs which are not specific enough to a geographical area
        trilats.append(result['trilat'])
        trilongs.append(result['trilong'])
        if len(trilats) >= 3:
            lat_dev = max(trilats) - min(trilats)
            long_dev = max(trilongs) - min(trilongs)

            eprint("Already got lat_dev = '%s' long_dev = '%s' from %d locations of '%s'" % (lat_dev, long_dev, len(trilats), ssid))
            if lat_dev > 0.1 and long_dev > 0.1:
                print("essid='%s' This SSID seems to be too common to be useful (lat_dev = '%s' long_dev = '%s'), skipping SSID" % (ssid, lat_dev, long_dev))
                return

        # Skip BSSIDs which are very dense on a small area
        if len(trilats) > 10:
            eprint("We already have more than 20 locations for ssid='%s', skipping" % (ssid))
            return

        address = 'Unknown'
        reverse_geocode_result = gmaps.reverse_geocode((result['trilat'], result['trilong']))
        time.sleep(1) # Makes google happy
        try:
            address = reverse_geocode_result[0]['formatted_address']
        except:
            eprint("Could not extract address from reverse geocoding results: '%s'" % (reverse_geocode_result))
            con.commit()
            con.close()

            sys.exit(1)

        eprint("netid='%s' channel='%s' ssid='%s' trilong='%s' trilat='%s' address='%s'" % (result['netid'], result['channel'], result['ssid'],
                                                                                                result['trilong'], result['trilat'], address))
        con.execute('insert or replace into essid_locations(transid, netid, channel, ssid, firsttime, lasttime, trilong, trilat, address) values(?,?,?,?,?,?,?,?,?)', (
            result['transid'], result['netid'], result['channel'], result['ssid'], result['firsttime'], result['lasttime'], result['trilong'], result['trilat'],
            address
        ))
        con.commit()

def wigle_has_no_results(ssid):

    cur = con.cursor()
    # Check if we already have this network
    cur.execute("select count(*) from ssid_no_results_cache where lower(ssid) = ?", (ssid.lower(),))
    count = int(cur.fetchone()[0])
    if count > 0:
        return True

    return False

def store_wigle_has_no_results(ssid):

    con.execute("insert or ignore into ssid_no_results_cache (ssid, lasttime) values (?,datetime('now'))", (ssid.lower(),))
    con.commit()

if googlemaps_api_key is not None:
    gmaps = googlemaps.Client(key=googlemaps_api_key)

try:
    con = sqlite3.connect(database_filename)
    con.text_factory = str

    # Create schema if not yet present
    con.executescript("""
    create table if not exists essid_locations (transid TEXT, netid TEXT, channel INTEGER, ssid TEXT,
    firsttime TEXT, lasttime TEXT, trilong REAL, trilat REAL, address TEXT);
    create table if not exists ssid_no_results_cache (ssid TEXT PRIMARY KEY, lasttime TEXT);
""")
    con.commit()

    s = requests.Session()
    api = 'https://wigle.net/api/v1/'
    s.post(api + 'jsonLogin', data = {'credential_0':login, 'credential_1':password, 'noexpire':'on', 'destination':''}) # wyszukiwanie dostępne tylko po zalogowaniu

    for ssid in sys.stdin:
        ssid = ssid.rstrip();

        if re.match('^hex:', ssid):
            eprint("essid='%s' is a binary SSID, need to skip it" % (ssid))
            continue

        eprint("essid='%s' checking in DB" % (ssid))
        
        cur = con.cursor()
        # Check if we already have this network
        cur.execute("select count(*) from essid_locations where lower(ssid) = ?", (ssid.lower(),))
        count = int(cur.fetchone()[0])
        if count > 0:
            eprint("essid='%s' we already have %d entries ,skipping" % (ssid, count))
            continue

        if wigle_has_no_results(ssid):
            eprint("Last wigle.net query returned no results for ssid='%s', skipping" % (ssid))
            continue

        r = s.post(api + 'jsonSearch', data = {'latrange1':'', 'latrange2':'', 'longrange1':'', 'longrange2':'', 'variance':'0.010', 'netid':'', 'ssid':ssid, 'lastupdt':'', 'addresscode':'', 'statecode':'', 'zipcode':'', 'Query':'Query'})

        jo = json.loads(r.text)
        eprint("essid='%s' : results='%s'" % (ssid, jo))

        if not jo['success']:
            eprint("API call for SSID '%s' has failed, results: %s" % (ssid, jo))
            if con:
                con.commit()
                con.close()
            sys.exit(1)

        eprint("SSID check for '%s' returned '%d' results" % (ssid, len(jo['results'])) )

        if len(jo['results']) == 0:
            store_wigle_has_no_results(ssid)
            continue

        add_ssid_results(jo['results'])

except sqlite3.Error as e:

    print ("Sqlite error '%s'" % (e.args[0]))

finally:

    if con:
        con.commit()
        con.close()

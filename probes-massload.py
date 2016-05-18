#!/usr/bin/env python2

# Written by Maciej Grela <enki@fsck.pl>

import sqlite3, json, sys

# Default config
database_filename = 'probes.sqlite'

try:
    con = sqlite3.connect(database_filename)

    # Create schema if not yet present
    con.executescript("""
    create table if not exists probe_requests (id INTEGER PRIMARY KEY, ts INTEGER NOT NULL, channel INTEGER, sta_mac TEXT, essid TEXT);
    -- create table if not exists routers (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
    -- create table if not exists interfaces (id INTEGER PRIMARY KEY, router_id INTEGER, name TEXT,
    -- UNIQUE (router_id, name), FOREIGN KEY(router_id) REFERENCES routers(id));
    -- create table if not exists interface_counters(iface_id INTEGER NOT NULL,
    -- timestamp INTEGER NOT NULL, rxb INTEGER, rxp INTEGER, txb INTEGER, txp INTEGER,
    -- UNIQUE (iface_id,timestamp), FOREIGN KEY(iface_id) REFERENCES interfaces(id));
""")
    con.commit()

    for line in sys.stdin:
        # print("Parsing line '%s'" % (line))

        probe_req = json.loads(line)

        if isinstance(probe_req, list):
            continue

        ts = probe_req['T']
        sta_mac = probe_req['addr2']
        channel = probe_req['channel']
        pkt_type = probe_req['type']
        pkt_subtype = probe_req['subtype']

        essid = None
        for ie in probe_req['ie']:
            if ie['id'] == 0 and len(ie['data']) > 0:
                try:
                    essid = ie['data'].decode('hex').decode('utf-8')
                except UnicodeDecodeError:
                    essid = "hex:%s" % (ie['data'])

        if essid is None:
            continue

        print("Probe @%s from %s on CH %d (type %d subtype %d) -> %s" % (ts, sta_mac, channel, pkt_type, pkt_subtype, essid))
        con.execute('insert into probe_requests(ts, channel, sta_mac, essid) values(?,?,?,?)', (ts, channel, sta_mac, essid))


except sqlite3.Error, e:

    print ("Sqlite error '%s'" % (e.args[0]))
    sys.exit(1)

finally:
    con.commit()

    if con:
        con.close()

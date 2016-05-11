#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) 2016 Adam Ziaja <adam@adamziaja.com> http://adamziaja.com

import sys
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
from scapy.all import *
import oursql

conn = oursql.connect(host='localhost', user='tapt', passwd='toor',
                      db='tapt', port=3307)
curs = conn.cursor(oursql.DictCursor)
curs.execute('CREATE TABLE IF NOT EXISTS probe (ID int NOT NULL AUTO_INCREMENT UNIQUE, ssid varchar(255) NOT NULL, mac varchar(17) NOT NULL, PRIMARY KEY (ID), UNIQUE KEY `probe` (`ssid`, `mac`))'
             )

def Handler(pkt):
    if pkt.haslayer(Dot11ProbeReq):
        # print pkt.summary()
        if len(pkt.info) > 0:
            print pkt.info, pkt.addr2
            try:
                curs.execute('INSERT IGNORE INTO `probe` (ssid, mac) VALUES (?, ?)'
                             , (pkt.info, pkt.addr2))
            except UnicodeDecodeError:
                pass

if len(sys.argv) == 2:
    sniff(offline=sys.argv[1], prn=Handler)
else:
    print('proszę podać w drugim argumencie plik *.cap lub *.pcap') # pcapng można przerobić na pcap przy pomocy komendy: editcap -F libpcap -T ether a.pcapng a.pcap

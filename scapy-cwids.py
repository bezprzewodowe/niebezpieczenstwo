#!/usr/bin/env python2

# Written by Maciej Grela <enki@fsck.pl>

from scapy.all import *
import json, time, sys

sniffer_iface = sys.argv[1]

class CWIDSFrame(Packet):
    name = 'CWIDS packet '
    fields_desc = [ ShortField("version", 1),
                    StrFixedLenField("Unknown1", "", 7),
                    ByteField("channel", 6),
                    StrFixedLenField("Unknown2", "", 6),
                    ShortField("original_length", 0),
                    FieldLenField("captured_length", 0),
                    StrFixedLenField("Unknown3", "", 8),
                    PacketLenField("dot11_frame", None, Dot11, length_from=lambda pkt: pkt.captured_length)
    ]

cwids_port = 1234

bind_layers(CWIDSFrame, CWIDSFrame)
bind_layers(UDP, CWIDSFrame, dport=cwids_port)

global i

def dump_probe_requests(packet):
    probe_requests = list()

    # print("++++++++++++++++++++++++++++++++++++")
    # packet.show()
    # print("++++++++++++++++++++++++++++++++++++")

    cwids_frames = packet[CWIDSFrame]
    while CWIDSFrame in cwids_frames:

        try:
            cwids_frame = cwids_frames[CWIDSFrame]
            cwids_frames = cwids_frames[CWIDSFrame].payload

            # print(cwids_frame.show());
            # print("Channel: %d" % ( cwids_frame.channel))
            # print("************************");

            dot11_frame = cwids_frame.dot11_frame

            if dot11_frame.type == 0 and dot11_frame.subtype == 4:
                frame_info = {
                    'T': time.strftime("%Y-%m-%dT%H:%M:%S+0000", time.gmtime()), 'channel': cwids_frame.channel,
                    'sc': dot11_frame.SC, 'type': dot11_frame.type, 'subtype': dot11_frame.subtype,
                    'addr2': dot11_frame.addr2, 'ie': list()
                }

                ie_set = dot11_frame[Dot11ProbeReq]
                while Dot11Elt in ie_set:
                    ie = ie_set[Dot11Elt]
                    frame_info['ie'].append( { 'id': ie.ID, 'data': ie.info.encode("hex") } )
                    ie_set = ie.payload

                print json.dumps(frame_info)
                # print dot11_frame[Dot11ProbeReq].show()
                # print("--------------------")
        except AttributeError:
            next

    return probe_requests

sniff(filter='port 1234', iface=sniffer_iface, prn=lambda packet: dump_probe_requests(packet), store=0)

#!/usr/bin/env python

"""
    example code to send a Insteon packet
    should be turned into a class one I work it out
"""
import sys


import argparse

from gen_packet import gen_packet, assemble_packet, b_to_binstr, pkt_crc
from parse_rf import print_insteon_rf_pkt, parse_insteon_rf_pkt

dstaddr=None
srcaddr=None
extpkt=None
hopsleft=None
hopsmax=None
invpkt=True
ackpkt=None
padpkt=False
grpaddr=None
bcastpkt=None
rawpkt=None
do_nothing=None
repeat_send=1;

debug=None

garage_light="163FE5"
test_switch="2B7811"

# this is grossly inefficient
def invert_pkt(p) :
    p=p.replace('0','A')
    p=p.replace('1','0')
    p=p.replace('A','1')
    return p


def mk_pkt(av=None) :
    global dstaddr
    global srcaddr
    global extpkt
    global hopsleft
    global hopsmax
    global ackpkt
    global grpaddr
    global bcastpkt
    global rawpkt
    global do_nothing

    pkt_args=dict()

    if grpaddr:
        pkt_args["grp"] = grpaddr
    elif dstaddr :
        pkt_args["dst"] = dstaddr
    else:
        #TODO: de-hardcode this
        pkt_args["dst"] = "2B7811"

    if srcaddr:
        pkt_args["src"] = srcaddr
    else:
        #TODO: de-hardcode this
        pkt_args["src"] = "13:25:80"


    if hopsleft:
        pkt_args["hopsleft"] = hopsleft

    if hopsmax:
        pkt_args["hops"] = hopsmax

    if extpkt:
        pkt_args["extended"] = extpkt

    if ackpkt:
        pkt_args["ack"] = actpkt

    if bcastpkt:
        pkt_args["bcast"] = bcastpkt

    pkt_args["cmd"] = av[:2]

    print >> sys.stderr, "pkt_args = ", pkt_args
    pkt = gen_packet( **pkt_args )

    return pkt


def read_raw_pkt(plist):
    a = list()
    for i in plist:
        if i == ":":
            continue
        a.append( int(i, 16) )

    return a

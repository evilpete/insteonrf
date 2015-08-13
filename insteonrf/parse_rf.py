#!/usr/bin/env python
"""
    primitive library for working with Insteon RF packets
"""

import sys
import datetime
from myexceptions import *

from print_packet import extract_insteon_flags, lookup_insteon_cmd, extract_insteon_addr, flag_str
from insteon_cmds import sd_cmd_list, ext_cmd_list, bc_sd_cmd_list, bc_ext_cmd_list

from gen_packet import pkt_crc, calc_ext_crc
from manchester import demanchester

debug = 1
be_verbose=1

of=None

startheader_i = "0011000101010101"
startheader = "1100111010101010"
startheadermark = 5

class Pkt(object) :
    def __init__(self, dat, timestp=None, offset=0) :
        """ 
        reads a raw packet in the form of a string of "1' & "0"
        """
        self.raw_dat = dat
        self.offset = dat
        self.validcrc = 0
        self.calc_crc = None

        if timestp is not None:
            self.timestamp = datetime.fromtimestamp(timestp)
        else:
            self.timestamp = datetime.datetime.now()

        self.time_str = self.timestamp.time().isoformat()
        self.dat = extract_pkt_data(self.raw_dat)

        if len(self.dat) >= 10:
            self.calc_crc = pkt_crc(self.dat)
        self.hex_str = self.pkt_simple()

    def pkt_simple(self) :
        try:
            if len(self.dat) < 4 :
                return ""
            h = ["{:02X}".format(x) for x in self.dat]
            a = [h[0], ":", " ".join(h[1:4]), ":", " ".join(h[4:7]),  ":", " ".join(h[7:23])]

            if len(h) > 22 :
                a.append(":")
                a.append(" ".join( h[23:]))

        except Exception, err:
            #pass
            print "err", err
            if self.dat: print "dat", self.dat
            #print "a", a
            if h: print "h", h
            raise

        return(" ".join(a))


#-----------------------

def pkt_simple(dat):
    h = ["{:02X}".format(x) for x in dat]
    a = ( h[0], ":", " ".join(h[1:4]), ":", " ".join(h[4:7]),  ":", " ".join(h[7:23]))

    if len(h) > 22 :
        a.append(":")
        a.append(" ".join( h[23:]))

    return(" ".join(a))


def get_pkt(dat, ts, verb=False) :
    """ returns list packet object """
    try:
        si = startIndex = dat.find(startheader, 0)

        if startIndex == -1 :
            si = startIndex = dat.find(startheader_i, 0)
        if si > -1 :
            if verb :
                print "Startheader_i Found"
            dat=dat.replace('0','A')
            dat=dat.replace('1','0')
            dat=dat.replace('A','1')

        if startIndex == -1 :
            # print "No startheader"
            return None

        header_len = len(startheader)
        data_len=len(dat)
        subpkt = list()
        pkt_list = list()

        prev_header = si
        si = dat.find(startheader, prev_header + header_len)
        while( si > 0 ) :
            subpkt.append( ( prev_header , si ) )
            prev_header = si
            si = dat.find(startheader, prev_header + header_len)
        else :
            subpkt.append( ( prev_header , data_len ) )

    except IndexError:
        print "Index Fail"
        return

    for sb in subpkt :
        try :
            pkt =  Pkt( dat[sb[0]:sb[1]], ts, sb[0]) 
        except ValueError, err :
            if be_verbose > 1 :
                print "ValueError",err
                # print "PKT = ", dat
            print ["{:02X}".format(x) for x in pkt_dat]
            continue
        else :
            pkt_list.append ( pkt )

    return pkt_list





#preamble =   "1001100111"

def extract_pkt_data(dat) :
    """
    reads a raw packet in the form of a string of "1' & "0"
    returns a string parsed data in the form of an array of ints 
    """

    i = 0
    if dat[startheadermark:startheadermark+2] == "11" :
        i=startheadermark

#    if debug :
#   print "dat :",  dat[:70]

    results = list()

    j = 0
    while ( dat[i:i+2] == "11" ) :
        i = i + 2
        try:
            dm = demanchester( dat[i:i+26] )
        except Exception, err :
            if len(results) >= 10 :
                if be_verbose :
                    print "demanchester Err, ignoring"
                break
                if be_verbose :
                    print "demanchester Err"
                    print results
                    print " ".join([ "{:02X}".format(j) for j in results ])
                    raise

        if len(dm) < 13 :
            break
        i = i + 26
        count_field = int(dm[4::-1], 2)
        dat_field   = int(dm[:4:-1], 2)

        results.append(dat_field)

    if debug >1  :
        print "{:2d} : {:5s} ({:2d}) : {:s} {:02X}".format(
        j,
        dm[4::-1], count_field,
        dm[:4:-1], dat_field)
        j = j + 1

    return results



def main() :
    print_insteon_pkt(raw_pkt)
    print

def parse_openlog(fname="sample_log.txt") :
    global of
    try:
        of = open(fname, 'a')
    except IOError, err:
        print "Could not open output file {!s}".format(fname)
        print err
    else :
        print "Logging to file", fname

def parse_flushlog() :
    if of is not None :
        of.flush()
    
def parse_closelog() :
    if of is not None :
        of.close()


def print_insteon_pkt(dat, verb=0, checkcrc=0, timestp=None) :
    """
    expects raw demodulated binary data in the form of a string of 1 & 0 
    will parse then dump packet data
    """
    global be_verbose

    be_verbose = verb

    pktlist = get_pkt(dat, timestp)


    if pktlist is None :
        if be_verbose :
            print "no valid packets in data"
            print "len=", len(dat), "dat=", dat[:30]
        return 0

#    if be_verbose :
#   print pkt.subpkt

    #if debug :
    # print "dat :",  dat[:70]

    for p in pktlist:
        # print pkt_dat
        if be_verbose :
            print p.hex_str
            r = parse_insteon_rf_pkt(p.dat)
            print_insteon_rf_pkt(r)
        else :
            #print "p.calc_crc", p.calc_crc
            if p.calc_crc is not None :
                cr="crc"
                w = 48
                if p.dat[0] & 0b00010000 : 
                    x = 23
                    w=106
                else :
                    x = 9

                if p.calc_crc != p.dat[x] :
                    cr="CRC"
                print "{0:<{width}} {1:s} {2:02X}".format(
                    p.hex_str,
                    cr,
                    p.calc_crc,
                    width=w
                )
            else :
                print p.hex_str
        if of is not None :
            print >> of, p.hex_str

    sys.stdout.flush()

    return len(pktlist)

def parse_insteon_rf_pkt(p) :
    """
    parse a packet (in the form of a string of "1" & "0")
    returns a dict relevant data

    """

    r = dict()

    #print p
    r["flags"] = extract_insteon_flags(p)
    r["cmd"] = lookup_insteon_cmd(p)
    r["dst"], r["src"] = extract_insteon_addr(p)

    # should this be native ints or in hex strings like the addresses
    r['hex'] = ["{:02X}".format( b ) for b in p]
    r['dat'] = p

    if ( r["flags"]["extended"] == 1 and len(p) >= 23 ) :
        r["crc"] = p[23]
        # print "CRC", p[22], r["crc"] 
        r["ext_crc"] = p[22]
        # print "C CRC", r["ext_crc"]
    else :
        r["crc"] = p[9]
        r["ext_crc"] = None

    return r

def print_insteon_rf_pkt(d):
    print "Packet len : {:d} bytes".format(len(d['hex']))

    fg = d["flags"]
    if fg["group"] :
        print d["dst"], "->", d["src"], ":", d["cmd"]
    elif d["src"] is not None :
        print d["src"], "->", d["dst"], ":", d["cmd"]
        print "\t", flag_str(d["flags"])
        #    print ":  {:28s} Extended={:d} Bcast={:d} Max_Hops={:d} Hops_Left={:d}".format(
        #       fg["mtext"], fg["extended"], fg["bcast"],  fg["maxhops"], fg["hopsleft"]),

    try :
        pks =  pkt_simple( d["dat"] )
        print pks
        # print "\t",d["hex"][0],
        #    except ValueError, err :
        #   continue

        # print ":", " ".join( d["hex"][1:4]),
        # print ":", " ".join( d["hex"][4:7]),
        # print ":", " ".join( d["hex"][7:])

    except ValueError, err :
        print "ValueError",err, d["hex"]

    if fg["extended"] and d["ext_crc"] is not None :
        e_crc = calc_ext_crc( d["dat"] )
        if d["ext_crc"] != e_crc :
            print "Ext CRC mismatch : {:02X} != {:02X}".format( d["crc"], d["calc_crc"] )

    if d["crc"] is not None :
        crc = pkt_crc( d["dat"] ) 
        if  d["crc"] != crc :
            print "CRC mismatch : {:02X} != {:02X}".format( d["crc"], crc )

    print "\n"


# -- testing --
def render_insteon_rf_pkt(d):
    fg = d["flags"]
    # if fg["group"] :
    #     print d["dst"], "->", d["src"], ":", d["cmd"]
    # elif d["src"] is not None :
    #     print d["src"], "->", d["dst"], ":", d["cmd"]
    #     print "\t", flag_str(d["flags"])
    #     print ":  {:28s} Extended={:d} Bcast={:d} Max_Hops={:d} Hops_Left={:d}".format(
    #     fg["mtext"], fg["extended"], fg["bcast"],  fg["maxhops"], fg["hopsleft"]),

    try:
        p.ks = pkt_simple( d["dat"] )
        print pks

    except ValueError, err :
        print "ValueError",err, d["hex"]

    if fg["extended"] and d["ext_crc"] is not None :
        e_crc = calc_ext_crc( d["dat"] )
        if d["ext_crc"] != e_crc :
            return "Ext CRC mismatch : {:02X} != {:02X}".format( d["crc"], d["calc_crc"] )

    if d["crc"] is not None :
        crc = pkt_crc( d["dat"] ) 
        if  d["crc"] != crc :
            return "CRC mismatch : {:02X} != {:02X}".format( d["crc"], crc )

def render_insteon_pkt(dat, verb=False, checkcrc=0, timestp=None) :
    """
    expects raw demodulated binary data in the form of a string of 1 & 0 
    will parse then dump packet data
    """
    out = list()
    pktlist = get_pkt(dat, timestp)

    if pktlist is None:
        if verb:
            print "no valid packets in data"
            print "len=", len(dat), "dat=", dat[:30]
        return

    for p in pktlist:
        if verb :
            print p.hex_str
            r = parse_insteon_rf_pkt(p.dat)
            print_insteon_rf_pkt(r)
        
        if p.calc_crc is not None:
            cr="crc"
            w = 48
        if p.dat[0] & 0b00010000: 
            x = 23
            w=106
        else:
            x = 9

        if p.calc_crc != p.dat[x] :
            cr="CRC"
            s = "{0:<{width}} {1:s} {2:02X}".format(
                p.hex_str,
                cr,
                p.calc_crc,
                width=w
                )
            out.append(s)
        else:
            out.append(p.hex_str)

        if of is not None :
            print >> of, p.hex_str

    sys.stdout.flush()
    return out

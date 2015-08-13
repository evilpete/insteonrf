#!/usr/local/bin/python
# 
# This is Junk code 
# written for (mostly) onetime use     
# for proof of concept
# 

from mdata import mdata
from decode import cksumbstr, hexstr
from insteon_cmds import sd_cmd_list, ext_cmd_list, bc_sd_cmd_list, bc_ext_cmd_list
import sys

no_short_pkt=1

# ((Not(sum of cmd1..d13)) + 1) and 255
def calc_crc(cmd, starti=7, endi=20) :
#    
    s = 0
    # print "calc_crc", cmd[starti:endi]
    for x in cmd[starti:endi] :
        #i = int(x, 2)
        # print "x = ", x, i, s
        s = s + x
#
    #print "s =", s
    s = ~s
    #print "~s =", s
    s = s + 1
    #print "~s +1 = ", s
    s = s & 255
    # print "(~s +1) & 255 = ", s
    return s

# Colors
def pink(t):    return '\033[95m' + t + '\033[0m'
def blue(t):    return '\033[94m' + t + '\033[0m'
def yellow(t):  return '\033[93m' + t + '\033[0m'
def green(t):   return '\033[92m' + t + '\033[0m'
def red(t):     return '\033[91m' + t + '\033[0m'

def extract_insteon_flags(dat=None, flag=None) :

    if flag is None :
        try :
            flag = dat[0]
            #flag = int(dat[5:13][::-1], 2)
        except ValueError, err :
            print  >> sys.stderr, "dat=", dat
            print  >> sys.stderr, "dat[0]=", dat[0]
            return None

    messsage_text = [ "Direct Message",
                      "ACK of Direct Message",
                      "Group Cleanup Direct Message",
                      "ACK of Group Cleanup Direct Message",
                      "Broadcast Message",
                      "NAK of Direct Message",
                      "Group Broadcast Message",
                      "NAK of Group Cleanup Direct Message",]
    ret = dict()

    ret["maxhops"]  = (flag & 0b00000011)
    ret["hopsleft"] = (flag & 0b00001100) >> 2
    ret["extended"] = (flag & 0b00010000) >> 4
    ret["ack"]      = (flag & 0b00100000) >> 5
    ret["group"]    = (flag & 0b01000000) >> 6
    ret["bcast"]    = (flag & 0b10000000) >> 7
    ret["mtype"]    = (flag & 0b11100000) >> 5
    ret["mtext"]    = messsage_text[ret["mtype"]]



    return ret 

def gen_packet(kwargs) :
        src_addr = kwargs.get("src", None)
        dst_addr = kwargs.get("dst", None)
        grp_addr = kwargs.get("grp", None)


def lookup_insteon_cmd(dat=None, cmd=None, ext=None, bcast=None) :
    subc = None
    if cmd is None :
        if len(dat) < 8 :
            return None

        c = dat[7]
        if len(dat) >= 9 :
            subc =  dat[8]
        ext = dat[0] & 0b00010000
        bcast = dat[0] & 0b10000000
    else :
        c = cmd

    cmd_list = sd_cmd_list

    if ext and bcast :
        cmd_list = bc_ext_cmd_list
    elif ext :
        cmd_list = ext_cmd_list
    elif bcast :
        cmd_list = bc_sd_cmd_list


    if c in cmd_list :
        if "subcmd" in cmd_list[c] and subc is not None and subc in cmd_list[c]["subcmd"] :
            return "{!s}{!s}".format(cmd_list[c]["label"], cmd_list[c]["subcmd"][subc])
        else :
            return cmd_list[c]["label"]
    else :
        return( "0x{:02X} {!s}".format(c, cmd_list["label"] ) )

    # fall through ( should never get here )
    return( "0x{:02X}".format(c) )
    
def extract_insteon_addr(dat) :

    addr1 = None
    addr2 = None

    if len(dat) > 4:
        addr1 = "{:02X}{:02X}{:02X}".format(dat[3], dat[2], dat[1])

    if len(dat) > 7:
        addr2 = "{:02X}{:02X}{:02X}".format(dat[6], dat[5], dat[4])

    return addr1, addr2

def extract_insteon_addr_old(dat) :
    ldat = len(dat)

    addr1 = None
    addr2 = None

    if ldat > 53 :
        a1 = dat[44:52][::-1]
        a2 = dat[31:39][::-1]
        a3 = dat[18:26][::-1]
        addr1 = "{:02X}{:02X}{:02X}".format(
                    int(a1, 2), int(a2, 2), int(a3, 2))


    if ldat > 91 :
        A3 = dat[57:65][::-1]
        A2 = dat[70:78][::-1]
        A1 = dat[83:91][::-1]
        addr2 = "{:02X}{:02X}{:02X}".format(
                    int(A1, 2), int(A2, 2), int(A3, 2))

    return addr1, addr2


def parse_insteon_rf_pkt(m) :
    """
        parse a packet (in the form of a string of "1" & "0")
        returns a dict relevant data

    """


    lm = len(m)

    # if it does not even have a src/dst addr
    if lm <= 91 :
        return None


    #if not m.startswith("11111") :
 #      return None

    r = dict()

    # r["dst"], r["src"] = extract_insteon_addr(m)


    try :
        r["data_byte_count"] = int(m[13:18][::-1], 2)
    except ValueError, err :
        print >> sys.stderr, "m=", m
        print >> sys.stderr,  "m[13:18][::-1]=", m[13:18][::-1]
        return None

    r["full_bit_count"] = ( 13 * (r["data_byte_count"] +1 ) ) + 5 
    r["actual_bit_count"] = lm


    # print "Flags:  {:s}, bcast={:d}, Max Hops={:d}, Hops Left={:d}".format(  [flags[s] for s in [ "mtext", "bcast", "maxhops","hopsleft" ]] )
#   print "{:3d}".format(lm),
    # print  m[:5] + " " + m[5:13] + " " + m[13:18] + " ........ " + m[26:31] + " ........ " + m[39:44] + " ........ " + m[52:57] + " ........ " + m[65:70] + " ........ " + m[78:83]  + " ........ " + m[91:96] \
#                + " " + m[96:104] + " " + m[104:109]  + " " +  m[109:117]  + " " + m[117:122] + " " +  m[122:130]  + " " + m[130:]

    # split packet up
    #
    # The decoded RF packet is of the form of a decrementing five bit count field followed by 8 hits of data.
    # All fields are in ordered LSB (least significant bit) first.
    #
    da = [ ]
    a = [ ]
    x = 0
    while x < lm :
        y = x
        x = x + 5
        a.append(m[y:x:])
        y = x
        x = x + 8
        s = m[y:x]
        if len(s) :
            a.append(m[y:x])
            da.append(int(m[y:x][::-1], 2))

    r["flags"] = extract_insteon_flags(da)
    r["cmd"] = lookup_insteon_cmd(da)
    r["dst"], r["src"] = extract_insteon_addr(da)

    print "{:3d} {:s}".format(lm, " ".join(a))

    # should this be native ints or in hex strings like the addresses
    r['hex'] = ["{:02X}".format( b ) for b in da]
    r['dat'] = da

    if ( r["flags"]["extended"] == 1 and len(da) >= 23 ) :
        r["crc"] = da[22]
        # print "CRC", da[22], r["crc"] 
        r["calc_crc"] = calc_crc(da)
        # print "C CRC", r["calc_crc"]
    else :
        r["crc"] = None
        r["calc_crc"] = None

    return r

# dirty dirty dirty
# no arg checking
# dirty dirty dirty
def flag_str(flg) :
    return "{:28s} Extended={:d} Bcast={:d} Max_Hops={:d} Hops_Left={:d}".format(
            flg["mtext"], flg["extended"], flg["bcast"],  flg["maxhops"], flg["hopsleft"])

def print_insteon_rf_pkt(d):

    # print "len :", fpl


    print "len : actual={:3d} {:3d}\t:\tfull={:3d} {:3d}".format(
            d["actual_bit_count"], (d["actual_bit_count"]/8),
            d["full_bit_count"], (d["full_bit_count"]/8) )

    if d["actual_bit_count"] < d["full_bit_count"] :
        print "len {:3d} < {:2d} short".format(d["actual_bit_count"], d["full_bit_count"])
        if no_short_pkt :
            print "\n"
            return

    by = ( d["actual_bit_count"] / 8 )
    print "bytes =", by
    bits = by * 28
    print "bits =", bits
    bitime_ms = bits * .110
    print "bitime_ms =", bitime_ms

    if d["src"] is not None :
        print d["src"], "->", d["dst"], ":", d["cmd"]
    fg = d["flags"]
    print "\t", flag_str(d["flags"]),
#    print ":  {:28s} Extended={:d} Bcast={:d} Max_Hops={:d} Hops_Left={:d}".format(
#           fg["mtext"], fg["extended"], fg["bcast"],  fg["maxhops"], fg["hopsleft"]),
    print "Packet len={:d}bits, Data={:d}bytes, pl={:d}".format( d["full_bit_count"] , (d["data_byte_count"] - 5), d["data_byte_count"])

    try :
        print "\t",d["hex"][0],
        print ":", " ".join( d["hex"][1:4]),
        print ":", " ".join( d["hex"][4:7]),
        print ":", " ".join( d["hex"][7:])
    except ValueError, err :
        print "ValueError",err, d["hex"]

    if fg["extended"] and d["crc"] is not None :
        if  d["calc_crc"] == d["crc"] :
            print "CRC match : {0:02X}".format( d["crc"] )
        else :
            print "CRC mismatch : {:02X} != {:02X}".format( d["crc"], d["calc_crc"] )

    print "\n"




def main() :
    for m in mdata :
        if m.startswith("Mark") :
            print "\n", m, "\n"
            continue
        if m.startswith("Stop") :
            break
        try :
            d = parse_insteon_rf_pkt(m)
            if d is not None :
                # print "\n", m, "\n"
                print_insteon_rf_pkt(d)
        except IOError, err :
            continue
         

if __name__ == "__main__":
    main()  
    exit(0)







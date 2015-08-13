#!/usr/bin/python
# 
# This is testing code 
# written for debuging binary output into the Insteon RF protocol
# 

from decode import hexstr
# from extract_dat_ln import extract_dat
from print_packet import extract_insteon_flags, flag_str, lookup_insteon_cmd
from gen_packet import pkt_crc, calc_ext_crc
# from manchester import demanchester


import sys, traceback


invert_dat=0

#def cksumbstr(b, siz=8, mask=255) :
#    """
#    Quick-n-dirty checksum of a binary string like "10101010"
#    """
#    ret = 0
#    a4 =  [ b[i:i+siz] for i in range(0, len(b), siz) ]
#    for h in a4 :
#       ret = ret + int(h, 2)
#    return (ret & mask)


#preamble =   "1001100111"
preamble = "0011001100111"
#preamble = "100110011001"


#
# a demanchester for debuging
#
def local_demanchester(s) :
    i = 1
    b =  list()
    slen = len(s)

    # Note that since 1 starts as "1"
    # we are testing the 2nd bit for '1' or '0'
    while(i < slen) :
        if s[i] == s[i-1] :
            print "sync error", i, s[i], "==", s[-1]
            return b
        if s[i] == "1" :
            b.append("1")
        else :
            b.append("0")
        i = i + 2

    return b


def uncode(Sout, mark=None) :

    if mark is None :
        print "mark missing"
        return  None, None

    slen = len(Sout)
    r = list()
    datl = list()
    cont = True
    completed = 0;

    j = 0
    while cont and mark < slen :
        markStr = Sout[mark: mark +2]

        if markStr != "11" :
            print "Mark Missed", markStr
            print "\t", Sout[mark -3: mark], Sout[mark: mark +2], Sout[mark +2: mark+44]
            break

#       if mark < 20 :
#           print "=\t11 01010101010110011010100110"
        pm = mark
        mark = mark + 2
        dat = Sout[mark : mark +26]
        mark = mark +26
        r.append(markStr)
        r.append(dat)
        dm = local_demanchester(dat)
        # print "dm", dm
        if dm is None :
            print "dm is None"
            break
        m = "".join(dm)

        #print "{:d}\t{:s} {:s} {:<3d} {:s} {:s} {:s}".format(
        #       pm, markStr, dat, cs, m, hexstr(dat, sep=''), hexstr(m, sep='') )

        if len(m) < 13 :
            print "len m < 13"
            break
        print "{:02d} {:d}\t{:s} {:s}".format(j, pm, markStr, dat),
        count_field = int(m[4::-1], 2)
        dat_field   = int(m[:4:-1], 2)
        datl.append(dat_field)
        print "{:5s} ({:2d}) : {:s} {:02X}".format(
                m[4::-1], count_field, 
                m[:4:-1], dat_field),
        if ( j == 0 ):
            d = extract_insteon_flags(flag=dat_field)
            print flag_str(d),
        elif ( j == 7 ) :
            print lookup_insteon_cmd(cmd=dat_field),
        elif ( count_field == 3 and d["extended"] == 0) :
            print "CRC",
            c = pkt_crc(datl)
            if dat_field == c :
                print "OK",
            else :
                # print "c", type(c), c
                # print "dat_field", type(dat_field), dat_field
                print "Fail {:02X} != {:02X}".format(dat_field, c),

        elif ( count_field == 9 and d["extended"] == 1) :
            print "extend CRC",
            c = calc_ext_crc(datl)
            if dat_field == c :
                print "OK",
            else :
                print "Fail {:X02} != {:X02}".format(dat_field, c),
        elif ( count_field == 8 and d["extended"] == 1) :
            print "packet CRC",
            c = pkt_crc(datl)
            if dat_field == c :
                print "eOK",
            else :
                print "e3_Fail {:02X} != {:02X}".format(dat_field, c),
        print
        j = j + 1
        if count_field == 0 :
            print "count_field = ", count_field
            completed=mark
            mark = pm
            break

    else :
        print "While done : cont =", cont, "mark=", mark, "<", slen



    # print "While done : cont =", cont, "mark=", mark, "<", slen

    print "Mark", mark
    print "Last Mark", Sout[mark -26:mark], Sout[mark: mark +2], Sout[mark +2: mark+28],
    print Sout[mark+28: mark+30], Sout[mark+30: mark+58]
    print "dat", ["{:02X}".format(x) for x in datl]
    return r, mark, completed


def dump_pkt(Sout) :

    slen=len(Sout)

    print "Len:", slen
    # print Sout
    # print "SHex : ", hexstr(Sout, sep='') 


    if slen < 100 :
        return

    # print "preamble =", len(preamble), preamble

    ddat = list()

    startheader="1100110011101010101010"
    # startheader="11101010101010"
    startheader_i="00010101010101"

    si = startIndex = Sout.find(startheader, 0)
    if si == -1 :
        print "No startheader"
        si = Sout.find(startheader_i, 0)
        if si > -1 :
            print "Startheader_i Found"
            Sout=Sout.replace('0','A')
            Sout=Sout.replace('1','0')
            Sout=Sout.replace('A','1')



    i = 0
    ppre = 0
    while i < slen :
        startIndex =  Sout.find(startheader, i)
        if startIndex == -1 :
            print "header not found :  i = {:d} len = {:d}".format(i, slen) 
            break
        print "Header   at {:4d} ({:3d})\t".format( startIndex, (startIndex - ppre)),
        ppre = startIndex
        if (startIndex > 0) :
            print Sout[startIndex - 6: startIndex],
        endamble = startIndex + len(startheader)  
        print Sout[startIndex: endamble],  Sout[endamble: endamble + 10],
        print "\t{:>4.3f}".format( startIndex * .110 )
        i = startIndex + len(startheader)

#    i = 0
#    ppre = 0
#    while i < slen :
#       startIndex =  Sout.find(preamble, i)
#       if startIndex == -1 :
#           print "preamble not found :  i = {:d} len = {:d}".format(i, slen) 
#           break
#       print "Preamble at {:4d} ({:3d})\t".format( startIndex, (startIndex - ppre)),
#       ppre = startIndex
#       if (startIndex > 0) :
#           print Sout[startIndex - 6: startIndex],
#       endamble = startIndex + len(preamble)  
#       print Sout[startIndex: endamble],  Sout[endamble: endamble + 10],
#       print "\t{:>4.3f}".format( startIndex * .110 )
#       i = startIndex + len(preamble)

    print "\n\nData Grok\n\n"

    print "100110011001 : {:s}".format( local_demanchester("100110011001"))

    pack_cnt = 0
    i = 0
    while i < slen :

        startIndex =  Sout.find(preamble, i)

        if startIndex == -1 :
            print "preamble not found :  i = {:d} len = {:d}".format(i, slen) 
            break

        pack_cnt = pack_cnt + 1
        print "\nstarting at Preamble at ", startIndex
        j = startIndex + len(preamble) -2
        # print "Pre", Sout[i:j], Sout[j: j +2], Sout[j +2: j+10]
        print "first marker at", j

        ddat.append( Sout[i:j] )

        dat, i, comp = uncode(Sout, j)
        # print "uncode :", len(dat), i, " ".join(dat)
        ds=""
        for de in dat :
            if de != "11"  : 
                ds = ds + de

        # mand = "".join( local_demanchester(ds))
        # if comp > 0 or len(dat) >= 50 : # len(mand) >= 160 
        #     print "Manch : \"{:s}\",".format(mand)
        # imand = "".join( [ "0" if x=="1" else "1" for x in mand ] )
        # print "MiHex : ", hexstr(imand, sep='') 


        ddat = ddat + dat

        if i is None :
            break

    else :
        print "While done : i={:d} < len={:d}".format( i, slen)

    print "sub packets = ", pack_cnt
    j = 0
    for l in ddat :
        j = j + len(l)
    # print "\nFull datlen:", j
    # print "Full :", len(ddat), i, " ".join(ddat)
    ds=""

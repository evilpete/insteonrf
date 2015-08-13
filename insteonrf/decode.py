#!/usr/local/bin/python
# 
# This is Junk code 
# written for onetime use     
# for proof of concept
# 

__author__ = "Peter Shipley"

import sys
import struct



# SDRSharp_20140819_015323Z_915000kHz_IQ_280CF1_on_2.4M_clip1.csv

asum = [ ]

# SDRSharp_20140819_015323Z_915000kHz_IQ_280CF1_on_2.4M_clip2.csv

def decode_m(s, inv=None, bad="both") :
    l = len(s)
    x = 0

    data = list(s)

    ret_array = [ ]

    while( x<l ) :
        if (x +1) >= len(data) :
            print "# odd bits"
            break

        if data[x] == data[x+1] :
            print "Bad data",
            if bad == "bit" :
                print "skipping bit", x, data[x]
                x = x + 1
            elif bad == "both" :
                print "skipping bits", x, data[x], data[x+1]
                x = x + 2

            continue


        if data[x] == "0" and  data[x+1] == "1" :
            if inv :
                ret_array.append("1")
            else :
                ret_array.append("0")
        elif data[x] == "1" and  data[x+1] == "0" :
            if inv :
                ret_array.append("0")
            else :
                ret_array.append("1")
        else :
            print "Bad data, skipping bits"
            # break

        x = x + 2
    return "".join(ret_array)


def hexstr(data, sep=' ') :
    bt = ""
    h = [ ]
    if data is None :
        data = self.datstream
    for x in xrange(0, len(data)) :
        bt = bt +  data[x]
 
        if ( (x % 4) == 3 ) :
            h.append( hex(int(bt, 2))[2:] )
            bt = ""
 
    return sep.join(h)

def cksumbstr(b, siz=8, mask=255) :
    """
    Quick-n-dirty checksum of a binary string like "10101010"
    """
    ret = 0
    if isinstance(b, list) :
        a4 = b
    else :
        a4 =  [ b[i:i+siz] for i in xrange(0, len(b), siz) ]
    for h in a4 :
        ret = ret + int(h, 2)
    return (ret & mask)


def print_bstr(b) :
    global asum

    print "m", len(b), b
    csum = cksumbstr(b)
    print "csum", csum
    a8 =  [ b[i:i+8] for i in xrange(0, len(b), 8) ]
    asum.append(str(csum))
    print "#8=", len(a8), " ".join( a8 )
#
#    BO = list()
#    bo = list()
#    for d in a8 :
#       print "d", d
#       xx = int(d,2)
#       print "i", type(xx), xx, int(xx)
#       xx = struct.unpack('<L',  struct.pack('>L', int(d, 2))[0])
#       print "I", type(xx), xx, int(xx)
#       # BO.append(hex(int(d, 2)))
#       #bo.append(hex(struct.pack('>I', int(d, 2))))
#    print "#BO=", " ".join( BO )
#    print "#bo=", " ".join( bo )
    print "bh:",
    for h in a8 :
        print h,
        print hex(int(h, 2)),
#
# Reverse
#    print
#    print "BH:",
#    for h in a8 :
#       print h[::-1],
#       print hex(int(h[::-1], 2)),

#    print
#    print "#m2=", " ".join(  [ b[i:i+2] for i in xrange(0, len(b), 2) ])
#    print "#mh=", hexstr(b)

#    a4 =  [ b[i:i+4] for i in xrange(0, len(b), 4) ]
#    print "#4="
#    for h in a4 :
#       print h,
#       print hex(int(h, 2)),
    print ""
    t = b[:]
    print "Shift:"
    #print "\t", hexstr(t)
    for x in xrange(10) :
        print x, "\t", hexstr(t, sep='')
        t =  t[1:]


def doit(ta) :
    global asum
    #print "doit"
    for s in ta :
        print ""
        print "=="
        print "length=", len(s)
        # cs = cksumbstr(s)
        # asum.append(str(cs))
        # print "csum=", cs
        # print "s", s
        # print "#=", " ".join(  [ s[i:i+2] for i in xrange(0, len(s), 2) ])
        # print hexstr(s)

        print ""
        print "Manchester"
        m = decode_m(s)
        print_bstr(m)

    #    print ""
    #    print "Manchester Reverse"
    #    mr = m[::-1]
    #    print_bstr(mr)

        print ""
        print "Manchester Inverted"
        m = decode_m(s, inv=True)
        print_bstr(m)

    #    print ""
    #    print "Manchester Inverted Reverse"
    #    mr = m[::-1]
    #    print_bstr(mr)

    print ""
    # print "asum = ", " ".join(asum)

def main() :
    # print "main"
    cslist = list()
    if len(sys.argv[1:]) == 0 :
        ta = a
    else :
        ta = sys.argv[1:]

    na = ""
    cnt = 0
    for a in ta:
        if a == "11" :
            # print "skip", a
            pass
        else :
            sm = cksumbstr(a)
            cslist.append(sm)
            # print cnt, sm, a
            cnt = cnt + len(a)
            na = na + a


#    if len(ta) == 2 :
#       b = int(ta[0], 2) ^ int(ta[1], 2)
#       print "b={:b}".format(b)

    print ""
    print "cslist", cslist
    print "na", na
    doit( [na] )

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
     main()
     exit(0)


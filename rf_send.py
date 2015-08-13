#!/usr/bin/python


import sys, traceback
import readline
#import rlcompleter
import time
import argparse


from rflib import *

no_xmit=True

def_fr=914950000
# fr=914944000
def_br=9124

invert_data=False

opt_debug = False
opt_verbose=True

def b_to_binstr(s, invert=False) :
    """
        Convert string of "101010" to binary string
    """
    ret = list()
    if opt_debug :
        s = s.translate(None, '-')
    # a8 =  [ s[i:i+8] for i in xrange(0, len(s), 8) ]
    print >> sys.stderr,  "s=",  len(s), [s[x:x+8] for x in range(0, len(s), 8)]
    sys.stderr.flush()
    try :
        if invert :
            r = bytearray(int(s[x:x+8], 2) ^ 0xFF for x in range(0, len(s), 8))
        else :
            r = bytearray(int(s[x:x+8], 2) for x in range(0, len(s), 8))

    except Exception, err :
        print err
        print "x =", x
        traceback.print_exc(file=sys.stdout)

    finally :
        return r




def parse_args():
    parser = argparse.ArgumentParser(
        description='Send insteon commands from rfcat')
    parser.add_argument('-v', '--verbose',
                        help='Increase debug verbosity', action='count')
    parser.add_argument('-i', '--invert',
                        help='Invert data',
                        action='store_true', default=False)
    parser.add_argument('-d', '--debug',
                        help='Log debugging messages',
                        action='store_true', default=False)

    args = parser.parse_args()
    return args

def init_rf( **kwargs ) :
    global opt_debug

    d = RfCat(debug=False)

    # print "rf_configure"
    # print "getMARCSTATE : ", d.getMARCSTATE()

    # # d.strobeModeIDLE()
    # print "getMARCSTATE : ", d.getMARCSTATE()

    if "debug" in kwargs :
        debug = 1


    fr = kwargs.get("freq", def_fr)

    d.setFreq( fr)
    if opt_debug  or opt_verbose:
        print  "setFreq"
        print "Freq = ", d.getFreq()

    d.setMdmChanBW(200000)
    # d.setMdmChanBW(220000)
    if opt_debug :
        print "bandwidth ", d.getMdmChanBW()

    br = kwargs.get("baud", def_br)
    d.setMdmDRate(br)
    if opt_debug  or opt_verbose:
        print "Baud  \t", d.getMdmDRate()

    d.setBSLimit(BSCFG_BS_LIMIT_12)
    if opt_debug :
        print "setBSLimit"

    d.makePktFLEN(58)
    #print  "makePktFLEN"


    # d.setMdmModulation(MOD_GFSK)
    d.setMdmModulation(MOD_2FSK)

    d.setMdmDeviatn(75000)

    # d.setMdmSyncWord(0x6666)

    # d.setPktPQT(1)
    # d.setMdmSyncMode(4) # SYNCM_CARRIER)
 

    # d.rf_configure(**ifo.__dict__)

    d.setMaxPower()

    if opt_debug :
        print  "RadioConfig : "
        d.printRadioConfig()

    return d

space_i="\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66"
space="\x99\x99\x99\x99\x99\x99\x99\x99\x99\x99\x99\x99\x99"


def send_pkt(d, s, n=1, r=1) :
    """
        send_pkt(rfcat_obj, sring, xmit_count, repeat_count) :
    """
    if opt_debug or opt_verbose :
        print "send_pkt=", len(s), s
    bs = b_to_binstr(s, invert_data)
    #  print "bs=", len(bs), bs
    if opt_debug :
        sbs = ''.join("{0:08b}".format(x) for x in bytearray(bs))
        print "sbs     =", len(sbs), sbs

    # for i in xrange(n -1) :
    #   bs = bs + space_i + bs

    # d.setModeRX()

    for i in xrange(r) :
        d.RFxmit( bs )
        time.sleep(60/1000)

    d.strobeModeIDLE()

def main() :

    d = init_rf()

    while True :
        try :
            sys.stdout.flush()
            line = sys.stdin.readline()
            # print len(line)
            if line.startswith("#") :
                continue 
            line = line.strip()
            if opt_debug :
                print "line : {:d} \"{:s}\"".format(len(line),line)
            if len(line) == 1 :
                continue 
            if not line :
                if opt_verbose :
                    print "Not Line"
                exit(0)
            # dump_pkt(line)
            send_pkt(d, line)
            sys.stdout.flush()

        except KeyboardInterrupt:
            break

        except Exception, err :
            print "Send Failed :\n\t",  err
            if opt_debug :
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60
            # raise

if __name__ == "__main__":
    args = parse_args()
    opt_debug = args.debug
    opt_verbose = args.verbose
    invert_data = args.invert
    if opt_debug or opt_verbose :
        print "opt_debug=", opt_debug, "opt_verbose", opt_verbose, "invert_data", invert_data
    main()
    exit(0)


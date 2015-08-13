#!/usr/bin/env python
import sys
from time import asctime, localtime
import argparse

# import rlcompleter
from rflib import *
# import readline
invert_data = False


def parse_args():
    parser = argparse.ArgumentParser(
        description='Read insteon commands from rfcat')
    parser.add_argument('-v', '--verbose',
                        help='Increase debug verbosity', action='count')
    parser.add_argument('-t', '--time',
                        help='Log time',
                        action='store_true', default=False)
    parser.add_argument('-i', '--invert',
                        help='Invert data',
                        action='store_true', default=False)
    parser.add_argument('-d', '--debug',
                        help='Log debugging messages',
                        action='store_true', default=False)

    args = parser.parse_args()
    return args


def configure_RfCat(debug=False, rf_debug=False, opt_verbose=False):
    d = RfCat(debug=False)
    d.setMdmChanBW(200000)
    if rf_debug:
        print  >> sys.stderr, "bandwidth ", d.getMdmChanBW()

    d.setMdmDRate(br)
    d.setBSLimit(BSCFG_BS_LIMIT_6)  # 0 3 6 12

    syncword = 0x99D5
    syncword_b = "{0:016b}".format(syncword)
    syncword_i = syncword ^ 0xFFFF
    syncword_ib = "{0:016b}".format(syncword_i)
    if rf_debug:
        print  >> sys.stderr, "# Syncword_i : {0:04X}  {1:s}".format(syncword_i, syncword_ib)
        print  >> sys.stderr, "# Syncword   : {0:04X}  {1:s}".format(syncword, syncword_b)
    # syncword = 0x9D55
    d.setMdmSyncWord(syncword_i)
    d.setMdmChanBW(200000)
    print  >> sys.stderr, "bandwidth ", d.getMdmChanBW()

    d.setFreq(fr)
    d.setMdmModulation(MOD_2FSK)
    d.setMdmDeviatn(75000)
    d.setPktPQT(0)

    # SYNCM_NONE: None
    # SYNCM_15_of_16: 15 of 16 bits must match
    # SYNCM_16_of_16: 16 of 16 bits must match
    # SYNCM_30_of_32: 30 of 32 sync bits must match
    # SYNCM_CARRIER: Carrier Detect
    # SYNCM_CARRIER_15_of_16: Carrier Detect and 15 of 16 sync bits must match
    # SYNCM_CARRIER_16_of_16: Carrier Detect and 16 of 16 sync bits must match
    # SYNCM_CARRIER_30_of_32: Carrier Detect and 30 of 32 sync bits must match
    d.setMdmSyncMode(SYNCM_CARRIER)

    if opt_verbose:
        d.printRadioConfig()

        print  >> sys.stderr, "# Freq Offset", d.getFsOffset()
        print  >> sys.stderr, "# FreqEst {:d}".format(d.radiocfg.freqest)
        fq, nm = d.getFreq()
        print  >> sys.stderr, "# Freq {:0.5f} {:s}".format(fq, nm)
        print  >> sys.stderr, "# Freq delta {:0.5f}".format(fq - fr)

    sys.stdout.flush()
    return d


def keystop(delay=0):
    return len(select.select([sys.stdin], [], [], delay)[0])


if __name__ == "__main__":
    args = parse_args()
    rf_debug = args.debug
    fr = 914950000
    br = 9124

    opt_verbose = args.verbose
    opt_print_time = 0
    opt_log_time = args.time
    invert_data = args.invert

    d = configure_RfCat(debug=False, rf_debug=rf_debug,
                        opt_verbose=opt_verbose)

    z = 0
    o = 0
    while not keystop():
        try:
            y, t = d.RFrecv(timeout=2000)
            s = ''
            if args.verbose or args.time:
                print
                print "# {:s}:{:s} Received:{:s}".format(z, asctime(localtime(t)), len(y))
            if invert_data:
                s = ''.join("{0:08b}".format(x ^ 0xFF) for x in bytearray(y))
            else:
                s = ''.join("{0:08b}".format(x) for x in bytearray(y))
            print s
            z = z + 1

        except ChipconUsbTimeoutException:
            o = 0
            if opt_verbose:
                print ".",
            sys.stdout.flush()

        except KeyboardInterrupt:
            print "Please press <enter> to stop"

        except IndexError:
            print "Index fail"

        finally:
            if o and opt_verbose:
                freqest = d.radiocfg.freqest
                fq, nm = d.getFreq()
                print  >> sys.stderr, "Freq {:0.5f} {:s}".format(fq, nm)
                print  >> sys.stderr, "Freq Offset", d.getFsOffset()
                print  >> sys.stderr, "FreqEst {:d}".format(freqest)
                print  >> sys.stderr, "LQI {:08b}".format(d.radiocfg.lqi)
                sys.stderr.flush()

    sys.stdin.read(1)

    d.setModeIDLE()

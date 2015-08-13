#!/usr/bin/env python
"""
example code to send a Insteon packet
should be turned into a class one I work it out
"""
import sys
import argparse

from insteonrf.send_comm import *

verbose=False

def init():
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
    global repeat_send
    global invpkt
    global padpkt
    global verbose

    parser = argparse.ArgumentParser(add_help=True,
        epilog="example:\n\t# ./send_comm.py -v -d 163FE5 -s 132580 13 00",
        description='generate a Insteon packet',

    )

    parser.add_argument("-d", "--dst", dest="dst",
                        default=None,
                        help="Destination Insteon address")

    parser.add_argument("-s", "--src", dest="src",
                        default=None,
                        help="Source Insteon address")

    parser.add_argument("-e", "--extended", dest="ext",
                        action='store_true',
                        help="Extended Packet")

    parser.add_argument("-i", "--invert", dest="inv",
                        action='store_true',
                        help="invert bits")

    parser.add_argument("-I", "--Invert", dest="inv",
                        action='store_false',
                        help="no invert bits")

    parser.add_argument("-c", "--count", dest="count",
                        type=int,
                        default=1,
                        help="repeat packet")

    parser.add_argument("-m", "--maxhops",
                        type=int,
                        default=None,
                        help="Max hops")

    parser.add_argument("-l", "--hopsleft", dest="hopsleft",
                        type=int,
                        default=None,
                        help="Remaining Hops Left")

    parser.add_argument("-a", "--ack", dest="ack",
                        default=None,
                        action='store_true',
                        help="ACK")

    parser.add_argument("--no-ack", dest="noack",
                        default=None,
                        action='store_true',
                        help="no ACK")

    parser.add_argument("-b", "--broadcast", dest="bcast",
                        action='store_true',
                        help="Broadcast Message")

    parser.add_argument("-g", "--group", dest="grp",
                        default=None,
                        help="Group Message")

    parser.add_argument("-v", "--verbose", dest="verb",
                        action='store_true',
                        help="Verbose")

    parser.add_argument("-p", "--pad", dest="pad",
                        action='store_true',
                        help="Pad Packet")

#    parser.add_argument("-h", "--help", dest="help",
#                        action='store_true',
#                        help="Print Help")

    parser.add_argument("-r", "--raw", dest="raw",
                        action='store_true',
                        help="Raw Packet")

    parser.add_argument("-n", "--noop", dest="do_nothing",
                        action='store_true',
                        help="Dont Send Pkt")

    args, unknown_args = parser.parse_known_args()

    if args.do_nothing:
        do_nothing = args.do_nothing

#    if args.help:
#       parser.print_help()
#       exit(0)

    if args.count:
        repeat_send = args.count

    if args.pad:
        padpkt = args.pad

    if args.verb:
        verbose = args.verb

    if args.inv:
        invpkt = args.inv

    if args.ack:
        ackpkt = args.ack
    elif args.noack :
        ackpkt = False

    if args.raw:
        rawpkt = args.raw
        #  return unknown_args

    if args.dst:
        dstaddr = args.dst

    if args.src:
        srcaddr = args.src

    if args.ext:
        extpkt = args.ext

    if args.hopsleft:
        hopsleft = args.hopsleft

    if args.maxhops:
        hopsmax = args.maxhops


    if args.grp:
        grpaddr = args.grp

    if args.bcast:
        bcastpkt = args.bcast

    if grpaddr and dstaddr:
        raise AssertionError("Can't have group and node dest addr")

    return (unknown_args)


def main():
    av = init()

    if rawpkt:
        if len(av) == 0:
            print >> sys.stderr, "option -r reqires 9 to 32 args in hex"
            exit(1)
        pkt = read_raw_pkt(av)
        if len(pkt) == 9:
            if verbose :
                print >> sys.stderr, "pkt", pkt
            pkt.append(pkt_crc(pkt))
            if padpkt :
                pkt.append(0x00)
                pkt.append(0x00)
                pkt.append(0xAA)
            if verbose :
                print >> sys.stderr, "pkt", pkt

        #
        # use args to modify raw packet
        #
        if ackpkt is not None :
            if ackpkt :
                pkt[0] |= 0b00100000
            else :
                pkt[0] &= 0b11011111

        if hopsleft is not None :
            pkt[0] |= ( hopsleft & 0b0011) << 2

    else:
        # pkt = mk_pkt(av)
        pkt = gen_packet(
                    ack=ackpkt,
                    src=srcaddr, dst=dstaddr,
                    hops=hopsmax, hopsleft=hopsleft,
                    cmd=av[:2])

    if debug or verbose :
        print >> sys.stderr, "pkt = ", pkt
        print >> sys.stderr, "pkt = ", [ "{:02X}".format(j) for j in pkt]
        print >> sys.stderr, "pkt len = ", len(pkt)
        sys.stderr.flush()

    p = assemble_packet(pkt)
    if invpkt is not None:
        p = invert_pkt(p)

    if debug or verbose :
        print >> sys.stderr, "pkt len = ", len(pkt)
        print >> sys.stderr, "pkt len = ", len(p)
        sys.stderr.flush()

    # print >> sys.stderr, "p=",  len(p), [p[x:x+8] for x in range(0, len(p), 8)]
    # sys.stderr.flush()
    print "{:s}".format(p * repeat_send)


if __name__ == "__main__":
    main()
    exit(0)

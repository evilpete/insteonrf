#!/usr/bin/python
"""
Break out a packet for debugging
"""
from insteonrf.split_pkt import dump_pkt
from insteonrf.extract_dat_ln import extract_dat
import sys
import traceback

def readfromfile(filen) :
    print "\n===========\n"
    print filen

    try :
        Sout = extract_dat(filen)
    except IndexError, err: 
        print "Extract failed :\n\t", filen, "\n\t",  err
        return

    dump_pkt(Sout)

def main():
    if len(sys.argv) == 1 or sys.argv[1] == "-":
        while True:
            try:
                sys.stdout.flush()
                line = sys.stdin.readline()
                # print len(line)
                if line.startswith("#"):
                    continue
                line.strip()
                print "line :", len(line)
                print line
                if len(line) == 1:
                    continue
                if not line:
                    # print "Not Line"
                    exit(0)
                dump_pkt(line)
                sys.stdout.flush()

            except KeyboardInterrupt:
                break

            except Exception, err:
                print "Extract Failed :"
                print "    ",  err
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60
                raise

    else:
        for av in sys.argv[1:]:
            try:
                readfromfile(av)
            except Exception, err:
                print "Extract Failed :"
                print "    ", av
                print "    ", err
                raise


if __name__ == "__main__":
    main()
    exit(0)

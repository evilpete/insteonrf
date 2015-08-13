#!/usr/bin/python
import sys
import time

from insteonrf.parse_rf import print_insteon_pkt
from insteonrf.parse_rf import parse_openlog
from insteonrf.parse_rf import parse_closelog
# from insteonrf.parse_rf import parse_flushlog

opt_print_time = 0
opt_verbose = 0
opt_log_pkt = 0
# opt_print_pkt = 1


for a in sys.argv:
    if a == "-v":
        opt_verbose += 1
    elif a.startswith("-t"):
        opt_print_time = 1
    elif a.startswith("-l"):
        opt_log_pkt = 1
    elif a.startswith("-nol"):
        opt_log_pkt = 0
    # elif a.startswith("-p"):
    #     opt_print_pkt = 1
    # elif a.startswith("-nop"):
    #    opt_print_pkt = 0

# print  >> sys.stderr, "p opt_print_time=", opt_print_time
# print  >> sys.stderr, "p opt_verbose=", opt_verbose
# print  >> sys.stderr, "p opt_log_pkt=", opt_log_pkt

sys.stderr.flush()
if opt_log_pkt:
    parse_openlog()

c = 0
while True:
    try:
        line = sys.stdin.readline()
        c += 1
        if line.startswith("#"):
            print line
            continue
        line.strip()

        if not line:  # EOF
            # print >> sys.stderr, "Not Line", c
            break

        if line[0] != "0" and line[0] != "1":
            print >> sys.stderr, "No 1 or 0", line[0]
            continue
        if len(line) == 1:
            print >> sys.stderr, "Len = 1"
            continue

        j = print_insteon_pkt(line, verb=opt_verbose)
        if j > 0:
            if (opt_print_time):
                print time.asctime(time.localtime())
                sys.stdout.flush()
                sys.stderr.flush()
        # print "pkt len = ", j
    except Exception, err:
        print "Extract Failed :\n\t",  err
        raise


if opt_log_pkt:
    parse_closelog()

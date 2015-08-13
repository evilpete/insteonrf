
"""
 
 This is Junk code 
 written for onetime use     
 for proof of concept
 
 checksum calc for Insteon
 see http://www.madreporite.com/insteon/i2cs.html

"""
 
from pk import pktl



ext_comms = [


    "02 35 02 2B 80 25 13               2E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 D2",
    "02 51 1C 06 23 19 70 1A 11         2F 00 01 01 0F FF 00 A2 00 19 70 1A FF 1F 01 5D",
    "00 00 XX XX XX 1F                  2E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 D2",
    "00 00 XX XX XX 1F                  2E 00 00 00 00 00 00 00 00 00 00 00 00 00 D2 81",
    "00 00 XX XX XX 1F                  6B 09 00 00 00 00 00 00 00 00 00 00 00 00 00 8C",
    "02 62 XX XX XX 1F                  6B 09 00 00 00 00 00 00 00 00 00 00 00 00 00 8C",
    "02 62 1B C5 E4 1F                  2E 00 01 00 00 00 00 00 00 00 00 00 00 00 00 D1",
    "02 62 1C 06 23 1F                  2F 00 00 00 0F FF 01 00 00 00 00 00 00 00 00 C2",
    "02 51 1C 06 23 19 70 1A 11         2F 00 01 01 0F FF 00 A2 00 19 70 1A FF 1F 01 5D",
    "02 62 1C 06 23 1F                  2F 00 00 00 0F F7 01 00 00 00 00 00 00 00 00 CA",
    "02 51 1C 06 23 19 70 1A 11         2F 00 01 01 0F F7 00 E2 01 19 70 1A FF 1F 01 24",
    "02 62 1C 06 23 1F                  2F 00 00 00 0F EF 01 00 00 00 00 00 00 00 00 D2",
    "02 51 1C 06 23 19 70 1A 11         2F 00 01 01 0F EF 00 00 00 00 00 00 00 00 00 D1",
]




# ((Not(sum of cmd1..d13)) + 1) and 255
def calc_sum(cmd) :
    print "cmd ", cmd

    check_sum_str = cmd[-2:]
    check_sum = int( check_sum_str, 16 )

    # print "check_sum:", check_sum_str, check_sum


    cmd_array = cmd.split()

    print cmd_array

    # seems we ignore everything but the data block
    # s = int(cmd_array.pop(0), 16)
    # print "s = ", s
    # s = s + int(cmd_array.pop(0), 16)
    # print "s = ", s
    
    print "Grok ", cmd_array[-16:-1]
    s = 0
    for x in cmd_array[-16:-1] :
        i = int(x, 16)
        # print "x = ", x, i, s
        s = s + i

    #print "s =", s
    s = ~s
    #print "~s =", s
    s = s + 1
    #print "~s +1 = ", s
    s = s & 255
    print "(~s +1) & 255 = ", s
    print "check_sum:", check_sum_str, check_sum
    print "check_sum={0:02X}".format(check_sum)
    print "check_sum={0:02X}".format(s)
    return check_sum


 
# ((Not(sum of cmd1..d13)) + 1) and 255
def calc_all(cmd) :
    # print "cmd ", cmd

    # print "check_sum:", check_sum_str, check_sum

    cmd_array = cmd

    # print "\t", cmd_array

    # seems we ignore everything but the data block
    # s = int(cmd_array.pop(0), 16)
    # print "s = ", s
    # s = s + int(cmd_array.pop(0), 16)
    # print "s = ", s
    
    # print "Grok ", cmd_array
    s = 0
    for x in cmd_array :
        i = int(x, 16)
        # print "x = ", x, i, s
        s = s + i

    #print "s =", s
    s = ~s
    #print "~s =", s
    s = s + 1
    #print "~s +1 = ", s
    s = s & 255
    # print "(~s +1) & 255 = ", s
    # print "\tcheck_sum={0:02X}".format(s)
    return s

# dat ['CF', '11', '78', '2B', '01', '00', '00', '11', '00', '3D', '00', '00', 'AA']
# dat ['CB', '11', '78', '2B', '01', '00', '00', '11', '00', 'F9', '00', '00', 'AA']



def main() :


    for i in xrange(0,9) :
        for j in xrange(i,9) :
            if  i == j :
                 continue

            for p in pktl :
                cks = p[9]
                ck = int(p[9],16)

                c = calc_all(p[i:j])
                if c == ck :
                    print "Hit", p[i:j]
                    print "{:s} : {:d}:{:d} : {:02X}".format(cks, i, j, c)
                    print p, "\n"


    exit(0)
    for c in ext_comms :
        calc_sum(c)
        print ""

#
# Do nothing
# (syntax check)
#
if __name__ == "__main__":
     main()
     exit(0)

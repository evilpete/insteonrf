"""
    primitive library for generating Insteon RF packets
"""

__author__ = "Peter Shipley"


debug=0



# Endian
# echo -n I | od -to2 | head -n1 | cut -f2 -d" " | cut -c6 
import sys

gr_on=['0B', 'E5', '3F', '16', '80', '25', '13', '11', '00', 'A3', '00', '00', 'AA']
gr_off=['0B', 'E5', '3F', '16', '80', '25', '13', '13', '00', 'A3', '00', '00', 'AA']


verbose=0
debug=0

def roundup(x, base=10): 
    return int((math.ceil(x / float(base))) * base)

class genPacket(object) :

    def __init__(self,  **kwargs):
        self.debug = 0
        self.rfcat = kwargs.get("rfcat", None) 

preamble = "0101010101";
long_preamble="010101010101010101010101010101010101010101010101"

def b_to_binstr(s, invert=False) :
    """
        Convert string of "101010" to binary string
    """
    ret = list()
    if debug :
        s = s.translate(None, '-')
    a8 =  [ s[i:i+8] for i in xrange(0, len(s), 8) ]
    if invert :
        r = bytearray(int(s[x:x+8], 2) ^ 0xFF for x in range(0, len(s), 8))
    else :
        r = bytearray(int(s[x:x+8], 2) for x in range(0, len(s), 8))

    return r


def manchester_encode(*args) :
    """
        manchester encode
            input  string of "1011" 
            output  string of "1011" 
    """
    return_bits = list()
    if debug :
        print "manchester_encode :", args
    # nest of for loops since args may be a list of strings
    for x in args :
        for y in x :
            for z in y :
                if z == "0" :
                    return_bits.append("10");
                elif z == "1" :
                    return_bits.append("01");
                elif z == "-" :
                    return_bits.append(z);
                else :
                    print "char=",z
                    raise ValueError("invalid bit '{:!s}'".format(z))

    return "". join(return_bits)



def assemble_packet(dat, firstmarker=1) :

    dat_len = len(dat)
    if verbose :
        print "len = ", dat_len
    if ( not ( dat_len >= 10 and dat_len <= 13)  and dat_len != 32) :
        print >> sys.stderr, "warn: len =", dat_len, ", should be 12 or 32\n"
        sys.stderr.flush()

    if debug :
        print dat
    if isinstance(dat[0], int) : 
        if debug :
            print "dat is int list"
        dat_int = dat[:]
    elif isinstance(dat[0], str) : 
        if len(dat[0]) == 8 :
            if debug :
                print "dat is str bin list"
            dat_int = [ int(x, 2) for x in dat ]
        else :
            if debug :
                print "dat is str hex list"
            dat_int = [ int(x, 16) for x in dat ]

    if debug :
        print dat_int
    ret = list();

    m = manchester_encode( preamble )
    #ret.append(m)
    ret.append(m)
    if debug :
        ret.append("-")

    dat_len = len(dat_int)

    if firstmarker == 1 :
        ret.append('11')
        if debug :
            ret.append("-")
        firstb = dat_int.pop(0)
        x = "{:08b}".format(firstb) [::-1] 
        m = manchester_encode("11111",  x)
        ret.append(m)
        if debug :
            ret.append("-")
        if firstb & 0b00010000 :
            c = 31
        else : 
            c = 11
    else : 
        c = dat_len -1

    for x in xrange( len(dat_int)  ) :
        rc = "{:05b}".format(c)[::-1]
        c = c - 1
        rx = "{:08b}".format(dat_int[x])[::-1]
        ret.append('11')
        if debug :
            ret.append("-")
        m = manchester_encode( rc, rx )
        ret.append(m)
        if debug :
            ret.append("-")


    m = manchester_encode( long_preamble )
    ret.append(m)

    #
    # make sure return string is by 9
    # pad as needed 

    # print >> sys.stderr, "len( "".join(ret) ) % 8 =", len( "".join(ret) ), (len( "".join(ret) ) % 8)
    ret_str = "".join(ret)
    x = (len(ret_str) % 8)
    if x :
        return ret_str + ret_str[:x]
    else :
        return ret_str


def addr_to_list(addr):
    a = [0, 0, 0]

    if isinstance(addr, str) :
        if len(addr) == 6 :
            a[0] = int(addr[4:6], 16)
            a[1] = int(addr[2:4], 16)
            a[2] = int(addr[0:2], 16)
            return(a)
        if len(addr) == 8 and  addr[2:3] == ":" :
            a[0] = int(addr[6:8], 16)
            a[1] = int(addr[3:5], 16)
            a[2] = int(addr[0:2], 16)
            return(a)
    elif isinstance(addr, (tuple, list) ) :
            a[0] = int(addr[2], 16)
            a[1] = int(addr[1], 16)
            a[2] = int(addr[0], 16)
            return(a)

    return None

            

def gen_packet(**kwargs) :
 
    dat = []
    mflag = 0;

    if debug :
        print >> sys.stderr, "gen_packet kwargs=", kwargs
        sys.stderr.flush()

    src_addr = kwargs.get("src", None) 
    dst_addr = kwargs.get("dst", None)
    grp_addr = kwargs.get("grp", None) 

    if src_addr is None :
        raise IsyValueError("src addr is required")
    if grp_addr is None and dst_addr is None :
        raise IsyValueError("grp_addr or dst_addr required")

    hops =  kwargs.get("hops", None) 
    hopsleft =  kwargs.get("hopsleft", 3) 
    extended =  kwargs.get("extended", 0) 
    bcast =  kwargs.get("bcast", 0) 
    ack =  kwargs.get("ack", 0) 
    # grp =  kwargs.get("grp", None) 
    cmd =  kwargs.get("cmd", None) 
    crc =  kwargs.get("crc", None) 
    if extended :
        edat =  kwargs.get("dat", [] ) 

    if hops is not None :
        mflag |= ( hops & 0b00000011 )
    else :
        mflag |= 0b00000011 

    if hopsleft is not None :
        mflag |= ( hopsleft & 0b00000011 ) << 2
    else :
        mflag |= 0b00001100 

    if extended :
        mflag |= 0b00010000

    if ack :
        mflag |= 0b00100000

    if bcast :
        mflag |= 0b10000000

    if grp_addr is not None:
        mflag |= 0b01000000

    dat.append(mflag)

    if grp_addr :
        dat.extend(addr_to_list(src_addr))
        dat.extend(addr_to_list(grp_addr))
    else :
        dat.extend(addr_to_list(dst_addr))
        dat.extend(addr_to_list(src_addr))

    if isinstance(cmd, list) :
        for c in cmd :
            if isinstance(c, str) :
                dat.append( int(c, 16) )
            else :
                dat.append( c )
        if len(cmd) < 2 :
            dat.append( 0 )
    elif isinstance(cmd, str) :
        dat.append( int(cmd, 16) )
        dat.append( 0 )
    elif isinstance(cmd, int) :
        dat.append( cmd )
        dat.append( 0 )

    if extended :
        full_len=32;
        dat.extend(edat)
        pl = len(dat)
        if pl < 22  :
            for  i in xrange(22 - pl) :
                dat.append( 0 )
        ext_crc = calc_ext_crc(dat)
        dat.append( ext_crc )

    else :
        full_len=13

    if crc is None :
        crc = pkt_crc(dat)

    dat.append(crc)

    pl = len(dat)
    if pl < full_len  :
        for  i in xrange(full_len - (pl + 1) ) :
            dat.append( 0 )
        dat.append( 0xAA )
    
    return dat


def p_array_hex(a) :
    l = [ ]
    for x in (a) :
        l.append( "{:02X}".format(x) )
    return "[" +  ",".join(l) + "]"


lsfr_table = [ 0x00, 0x30, 0x60, 0x50, # 0 1 2 3
      0xC0, 0xF0, 0xA0, 0x90, # 4 5 6 7
      0x80, 0xB0, 0xE0, 0xD0, # 8 9 A B
      0x40, 0x70, 0x20, 0x10] # C D E F


def pkt_crc(dat):
    """
        calc packet CRC

        takes an instion packet in form of a list of ints
        and returns the CRC for RF packet

        This uses a table lookup to effectivly doing:
            r ^= dat[i] ;
            r ^= (( r ^ ( r << 1 )) & 0x0F) << 4 ;
            
    """

    # check if this is an short packet or extended packet
    if ( dat[0] & 0b00010000 ) :
        crc_len = 23
    else :
        crc_len= 9

    r = 0
    for i in dat[:crc_len] :
        r ^= i
        r ^= lsfr_table[ r & 0x0F ] 

    return r

# ((Not(sum of cmd1..d13)) + 1) and 255
def calc_ext_crc(cmd, starti=7, endi=22) :
    """
        calc checksum of extended packet data

        takes an instion packet in form of a list of ints
        and returns the CRC extended packet data

        using :
            ((Not(sum of cmd1..d13)) + 1) and 255

    """
    
    s = 0
    for x in cmd[starti:endi] :
        s = s + x

    s = ~s
    s = s + 1
    s = s & 255
    return s

if __name__ == "__main__":
    """
        Lib test Assertions
    """
    print "Test :"

    # note: packet order 
    pkt_test_dat = [
        (0x93, [0x07, 0x11, 0x78, 0x2B, 0x80, 0x25, 0x13, 0x11, 0x01, 0x93, 0x00, 0x00]), # Test gen_packet
        (0x58, [0x2B, 0x80, 0x25, 0x13, 0x11, 0x78, 0x2B, 0x11, 0xF6, 0x58]),
        (0xAF, [0x1B, 0x35, 0x02, 0x2B, 0x80, 0x25, 0x13, 0x2F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xD0, 0xAF]) ,
        (0xD3, [0x15, 0x80, 0x25, 0x13, 0x11, 0x78, 0x2B, 0x2F, 0x00, 0x00, 0x01, 0x0F, 0xFF, 0x00, 0xA2, 0x00, 0x13, 0x25, 0x80, 0xFF, 0x1F, 0x01, 0x49, 0xD3, 0xAA, 0xDD, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA]),

    ]

    print "\tpkt_crc"
    # test pkt_crc
    for p in pkt_test_dat :
        crc = pkt_crc(p[1])
        if crc != p[0] :
            raise AssertionError(
                "Bad CRC from pkt_crc\n\t{:s} : {:02X} != {:02X}".format(
                    " ".join([ "{:02X}".format(j) for j in p[:-1] ]), p[0], crc)
            )




    print "\tgen_packet"
    # Test gen_packet
    p = gen_packet(hops=3, hopsleft=1, src="132580", dst="2B7811", cmd=[0x11, 0x01] )
    ps =  " ".join([ "{:02X}".format(j) for j in p ]) 
    pkt_ok =  " ".join([ "{:02X}".format(j) for j in pkt_test_dat[0][1] ]) 
    if ps != pkt_ok :
        raise AssertionError(
                "gen_packet bad packet\n\t{:s} =! {:s}".format( ps, pkt_ok)
            )

    print "\tcalc_ext_cr"
    # test calc_ext_crc
    for p in pkt_test_dat :
        if len(p[1]) < 20 :
            continue
        ext_packet = p[1]
        ext_crc_ok = ext_packet[22]

        ext_crc = calc_ext_crc(ext_packet)

        if ext_crc != ext_crc_ok :
            raise AssertionError(
                "Bad CRC from calc_ext_crc\n\t{:s} : {:02X} != {:02X}".format(
                    " ".join([ "{:02X}".format(j) for j in ext_packet ]), ext_crc, ext_crc_ok)
            )

    print "\tmanchester_encode"
    # text manchester decode
    dm = "0101011010010101"
    x =  manchester_encode("11100111")
    if x != dm :
        raise AssertionError (
            "manchester_encode  test error \n\t{:s} =! {:s}".format( dm, x))

    print "\tto_binstr"
    # text manchester decode
    import binascii
    p = "000000010010001101000101011110001001101010111100110111101111"
    bs = b_to_binstr(p)
    if bs != "\x01\x23\x45\x78\x9a\xbc\xde\x0f" :
        raise AssertionError( "b_to_binstr fail\n")
    # inverted: fedcba87654321f0
    # bs = b_to_binstr(p, 1)

    print "\taddr_to_list"
    # Test addr_to_list
    a = addr_to_list("01:02:03")
    if a != [3, 2, 1] :
        raise AssertionError( "addr_to_list fail\n")

    import __main__
    print(__main__.__file__), ": syntax ok"

    exit(0)





Insteon Packet encoding format :

    Packet encoding example

    The short Packet Fields are 
        Flags     = byte 0
        To Addr   = byte 1 2 3
        From Addr = byte 4 5 6
        Command   = byte 7
        Cmd Arg   = byte 8
        Pkt CRC   = byte 9
        pad 00    = byte 10 11 ( optional )
        pad AA    = byte 12    ( optional )

    Extended packets are the same as short packets but have 14 byte payload instead of 2 byte 
    and have an extra CRC for the data.

    Extended packet Fields are :
        Flags     = byte 0
        To Addr   = byte 1 2 3
        From Addr = byte 4 5 6
        Command   = byte 7
        Cmd Arg   = byte 8
        Ext Data  = byte 9 through 21
        Data CRC  = byte 22
        Pkt CRC   = byte 23
        Pad AA    = byte 24 through 31 ( optional )


    To transmit the short packet :
        '0B', 'E5', '3F', '16', '80', '25', '13', '11', 'BF', '5F', '00', '00', 'AA'

    Giving the fields the values :
        Flag      = OB = Direct Message Max_Hops=3 Hops_Left=2
        To Addr   = 163FE5
        From Addr = 132580
        Command   = 11 = "Turn On"
        Cmd Arg   = BF = Level 191/255 ( 70% )
        CRC       = 5F

    Each byte (X) is encoded as 26 bits: 
        '11' followed by
        5 bit index number (manchester encoded
        8 bit byte (manchester encoded

    All values are written in LSB format (Least Significant Bit first)

    The first byte is always transmitted with a index of 32 ( 11111 )
    all following bytes are transmitted with a decrementing count


    Dat   index dat         LSB index dat     manchester                     '11' + manchester
    03 -> 11111 00000011 -> 11111 11000000 -> 0101010101 0101101010101010 -> 1101010101010101101010101010
    E5 -> 01011 11100101 -> 11010 10100111 -> 0101100110 0110011010010101 -> 1101011001100110011010010101
    3F -> 01010 00111111 -> 01010 11111100 -> 1001100110 0101010101011010 -> 1110011001100101010101011010
    16 -> 01001 00010110 -> 01010 11111100 -> 0110100110 1001011001101010 -> 1101101001101001011001101010
    80 -> 01000 10000000 -> 00010 00000001 -> 1010100110 1010101010101001 -> 1110101001101010101010101001
    25 -> 00111 00100101 -> 11100 10100100 -> 0101011010 0110011010011010 -> 1101010110100110011010011010
    13 -> 00110 00010011 -> 01100 11001000 -> 1001011010 0101101001101010 -> 1110010110100101101001101010
    11 -> 00101 00010001 -> 10100 10001000 -> 0110011010 0110101001101010 -> 1101100110100110101001101010
    BF -> 00100 10111111 -> 00100 11111101 -> 1010011010 0101010101011001 -> 1110100110100101010101011001
    D7 -> 00011 11010111 -> 11000 11101011 -> 0101101010 0101011001100101 -> 1101011010100101011001100101
    00 -> 00010 00000000 -> 01000 00000000 -> 1001101010 1010101010101010 -> 1110011010101010101010101010
    00 -> 00001 00000000 -> 10000 00000000 -> 0110101010 1010101010101010 -> 1101101010101010101010101010
    AA -> 00000 10101010 -> 00000 01010101 -> 1010101010 1001100110011001 -> 1110101010101001100110011001


    before transmission bit values are inverted/swapped ( that is 1=0 and 0=1 )

    The Full packet looks like

        preamble + encoded bytes ( inverted )

        10101010 + 0010101010101010010101010101 + 0010101010101010010101010101 + 0010100110011001100101101010 + 0001100110011010101010100101 + 0010010110010110100110010101 + 0001010110010101010101010110 + 0010101001011001100101100101 + 0001101001011010010110010101



=====

Every packet has a CRC byte at the end :

    Insteon documents the CRC as 7-bit linear-feedback shift register
    but is not a true shift register 

    the algorithm is :

    For each byte:
        Xor it with the running checksum
        Xor the upper nibble with the lower nibble
        Shift lower nibble by one then Xor with upper nibble


        r = 0 ;
        for(i=0;i<dat_len;i++) {
           r ^= dat[i] ;
           r ^= (( r ^ ( r << 1 )) & 0x0F) << 4 ;
        }

=====

Extended packets have a 2nd CRC

    The checksum is based on the twos complement of the sum of byte 7 though 22 ( cmd byte, opt byte and data bytes )

    the algorithm is :

    For bytes 7 though 22:
	take the sun of all the values 
	take two's complement Operator ( 'flipping' the bits)
	logical AND with 0xFF ( for a single byte result )


       r = 0 ;
       for(i=7;i<22;i++)
           r += dat[i] ;
           
       r = ~r ;
       r += 1 ;
       r = r & 0xFF ;
       

=====

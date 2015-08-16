# Tools for Insteon's RF protocol #

----

This code is meant as a proof of concept for the encoding and decoding of the Insteon RF protocol


For Protocol Information see [Doc/pkt_format.txt](Doc/pkt_format.txt)

Cracking the CRC :  [Reverse-Engineering a CRC](http://make-it-hack.blogspot.com/2015/08/reverse-engineering-crc.html)


----

## Hardware ##

The Hardware used here can be
[rtlsdr](http://sdr.osmocom.org/trac/wiki/rtl-sdr) style dongles or
[hack-rf](https://greatscottgadgets.com/hackrf/), or any device streaming 8bit Inphase Quadrature data

There is also support for using the
[cc1111emk868](http://www.ti.com/tool/cc1111emk868-915) usb donngle with
[rfcat](https://bitbucket.org/atlas0fd00m/rfcat)

----

## Data Format ##

Raw data files are either signed or unsigned 8 bit IQ [Inphase Quadrature](https://en.wikipedia.org/wiki/In-phase_and_quadrature_components) data 
Intermediate data is exchanged as ASCII strings of "1" and "0" with packets broken up with newlines,
empty and lines starting with '#' are ignored or treated as meta data.

Thus removing any problems with bit or byte order as well as bit or word alignment.

( This is modeled after Jef Poskanzer's [NetPBM](http://en.wikipedia.org/wiki/Netpbm_format) data transfer solution )


----

## Files ##

    fsk2_demod          a generic FCK2 demodulator 
    fsk2_mod            a generic FCK2 modulator  (BROKEN)

    rf_clip             reads IQ input and breaks data into packets with super lame squelch algorithm
    print_pkt.py        reads ASCII binary decodes Insteon packet
    split_pkt.py        Verbose Diag tool for looking at packet I/O

    send_comm.py        generates Insteon packet in ASCII binary

    rf_send.py	        transmits data with Rfcat input ASCII binary
    hackrf_xmit.sh      script to transmit with hack-rf

    rf_reciv.py	        receive data and demodulate with Rfcat ( outputs ASCII binary )
    rtl_reciv.sh        receive data with rtl-sdr dongle ( output unsigned 8 bit )
    hackrf_reciv.sh     receive data with hackrf ( output signed 8 bit )**  
    ** hackrf_reciv requires mod hackrf_transfer to write to stdout 

python libs (work in progress ) :  

>  insteon_cmds.py      Lookup table for insteon commands
>  manchester.py        many different manchster encoding funtions 
>  parse_rf.py          functions to parse ascii IO streams  
>  gen_packet.py        generate or process packets


S/plot*.png         plots of FSK demod

----

### External Libs ###

[liquid-dsp](http://liquidsdr.org/) is needed for fsk2_mod 

----

## Example use ##

Assuming you successfully compiled the demodulator 

    ./fsk2_demod -U < Dat/41802513110D2711018C00.dat  | ./print_pkt.py

should print :

    41 : 80 25 13 : 11 0D 27 : 11 01 8C 00           crc 8C

### Receive ###
 
>  `./rtl_reciv.sh | ./fsk2_demod | ./print_pkt.py` 
>
>  `./rf_reciv.py | ./print_pkt.py`
>
>  `./hackrf_reciv.sh | ./fsk2_demod | ./print_pkt.py`  
>  ( requires mod to hackrf_transfer to write to stdout )

### Transmit ###

>  `./send_comm.py -r 07 : E5 3F 16 : 80 25 13 : 11 BF 13 00 00 AA | ./fsk2_mod | ./hackrf_xmit.sh`
>
>  `./send_comm.py -r 07 : E5 3F 16 : 80 25 13 : 11 BF 13 00 00 AA | ./rf_send.py`
>
>  `./send_comm.py -d 163FE5 -s 132580 13 00 | ./rf_send.py`


[![Analytics](https://ga-beacon.appspot.com/UA-65834265-1/evilpete/insteonrf)]

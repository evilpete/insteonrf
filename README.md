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

    fsk2_mod            a generic FCK2 modulator  (BROKEN)

    rf_clip             reads IQ input and breaks data into packets with super lame squelch algorithm
    print_pkt.py        reads ASCII binary decodes Insteon packet
    split_pkt.py        Verbose Diag tool for looking at packet I/O

    send_comm.py        generates Insteon packet in ASCII binary

    rfcat_send.py	        transmits data with Rfcat input ASCII binary
    hackrf_xmit.sh      script to transmit with hack-rf

    rfcat_reciv.py	        receive data and demodulate with Rfcat ( outputs ASCII binary )
    <!--- rtl_reciv.sh        receive data with rtl-sdr dongle ( output unsigned 8 bit ) --->
    <!--- hackrf_reciv.sh     receive data with hackrf ( output signed 8 bit )**  --->
    ** hackrf_reciv requires mod hackrf_transfer to write to stdout 

python libs (work in progress ) :  

>  insteon_cmds.py      Lookup table for insteon commands
>  manchester.py        many different manchster encoding funtions 
>  parse_rf.py          functions to parse ascii IO streams  
>  gen_packet.py        generate or process packets


S/plot\*.png         plots of FSK demod

----

### External Libs ###

[liquid-dsp](http://liquidsdr.org/) is needed for fsk2_mod 

----

## Example use ##

rtl_433 -s 1024k  -F json -r  g004_915M_1024k.cu8

```json
{"time" : "@0.072767s", "model" : "Insteon", "pkt_type" : "Group Cleanup Direct Message", "from_id" : "2B7811", "to_id" : "226B3F", "command" : "13 01 ", "extended" : 0, "hops" : "3 / 3", "formatted" : "4F : 226B3F : 2B7811 : 13 01  79", "mic" : "CRC", "payload" : "4F3F6B2211782B130179"}
{"time" : "@0.072767s", "model" : "Insteon", "pkt_type" : "Group Cleanup Direct Message", "from_id" : "2B7811", "to_id" : "226B3F", "command" : "13 01 ", "extended" : 0, "hops" : "3 / 2", "formatted" : "4B : 226B3F : 2B7811 : 13 01  BD", "mic" : "CRC", "payload" : "4B3F6B2211782B1301BD"}
{"time" : "@0.072767s", "model" : "Insteon", "pkt_type" : "Group Cleanup Direct Message", "from_id" : "2B7811", "to_id" : "226B3F", "command" : "13 01 ", "extended" : 0, "hops" : "3 / 1", "formatted" : "47 : 226B3F : 2B7811 : 13 01  F1", "mic" : "CRC", "payload" : "473F6B2211782B1301F1"}
{"time" : "@0.072767s", "model" : "Insteon", "pkt_type" : "Group Cleanup Direct Message", "from_id" : "2B7811", "to_id" : "226B3F", "command" : "13 01 ", "extended" : 0, "hops" : "3 / 0", "formatted" : "43 : 226B3F : 2B7811 : 13 01  35", "mic" : "CRC", "payload" : "433F6B2211782B130135"}
```



### Receive ###
 
use [rtl_433](https://github.com/merbanan/rtl_433) to recive and decode

>  rtl_433 -s 1024k -R 154 -F json

use [rtl_433](https://github.com/merbanan/rtl_433) to recive raw data and decode with [./swpkt.py](swpkt.py)

>  rtl_433 -X 'n=Insteon_F16,m=FSK_PCM,s=110,l=110,t=15,g=20000,r=20000,invert,match={16}0x6666' | [./swpkt.py](swpkt.py)

>
>  `./rfcat_reciv.py | ./print_pkt.py`
>

### Transmit ###

>  `./send_comm.py -r 07 : E5 3F 16 : 80 25 13 : 11 BF 13 00 00 AA | ./fsk2_mod | ./hackrf_xmit.sh`
>
>  `./send_comm.py -r 07 : E5 3F 16 : 80 25 13 : 11 BF 13 00 00 AA | ./rfcat_send.py`
>
>  `./send_comm.py -d 163FE5 -s 132580 13 00 | ./rfcat_send.py`


[![Analytics](https://ga-beacon.appspot.com/UA-65834265-1/evilpete/insteonrf)]

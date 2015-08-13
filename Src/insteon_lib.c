char static_string[]="Author Peter Shipley   2015\n";
/* 
This is Junk code
written for onetime use
be happy if it only seg faults on you

--

toolbox library routines for inteon protocal

*/

#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <string.h>
#include <libgen.h>
#include <limits.h>
#include <sys/cdefs.h>
/* #include <sys/syslimits.h> */
#include <string.h>
// #include <math.h>

#ifndef __BYTE_ORDER__ 
#define __ORDER_LITTLE_ENDIAN__ 1234
#define __BYTE_ORDER__ __ORDER_LITTLE_ENDIAN__
#endif

 


/* for packet CRC  calc */
unsigned char lsfr_table[] = { 0x00, 0x30, 0x60, 0x50, // 0 1 2 3
			  0xC0, 0xF0, 0xA0, 0x90, // 4 5 6 7
			  0x80, 0xB0, 0xE0, 0xD0, // 8 9 A B
			  0x40, 0x70, 0x20, 0x10}; // C D E F


/* 0b00010000 = 0x10
   0b00001000 = 0x08
*/
#define PKT_EXT_FLAG 0x10



int pkt_crc(int dat_len, unsigned char dat[] ) {
    int i;
    int r;

    r = 0;
    for(i=0;i<dat_len;i++) {
        r ^= dat[i];
        r ^= lsfr_table[ r & 0x0F ] ;
    }

    return(r);
}

/*
    calc packet CRC
    takes an instion packet in form of a list of ints
    and returns the CRC for RF packet

    WARNING : This code is does not check array len
*/
int calc_pkt_crc( unsigned char dat[] ) {
    int crc_len = 9;

    /* test that we have an extended packet */
    if ( dat[0] & PKT_EXT_FLAG ) {
        crc_len = 23;
    } else {
        crc_len= 9;
    }

    return ( pkt_crc(crc_len, dat));
}

/*
    calc checksum of extended packet data

    takes an instion packet in form of a list of ints
    and returns the CRC extended packet data

    using :
	((Not(sum of cmd1..d13)) + 1) and 255

    WARNING : This code is does not check array length

*/
    
int calc_ext_crc(unsigned char dat[] ) {
    int j;
    int i;

    /* test that we have an extended packet */
    if ( ! ( dat[0] & PKT_EXT_FLAG )) {
        return(0);
    }

    j = 0;
    for(i=7;i<22;i++) {
	j = j + dat[i];
    }

    j = ~j;
    j = j + 1;
    j = j & 0xFF;
    return(j);
}
 
 
int roundUp(int numToRound, int multiple) { 
    if(multiple == 0) { 
	return numToRound; 
    } 

    int remainder = numToRound % multiple;

    if (remainder == 0)
	return numToRound;

    return numToRound + multiple - remainder;
}


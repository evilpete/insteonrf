char static_string[]="Author Peter Shipley   2015\n";
/* 

	A simple program for reading 8 bit I/Q data
	and demodulating fsk 

	Given that :
	    If I leads Q we know the carrier higher then the sample freq
	    If Q leads I we know the carrier lower then the sample freq

	and knowing the baud rate
	we can demodulate the data by taking samples every "bit width"
	and check the phase relationship between I & Q

	This is Junk code written for (mostly) onetime use for proof of concept

*/

#include <math.h>

#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

#include<stdio.h>
#include<stdint.h>
#include<string.h>

#include <time.h>

uint16_t fxpt_atan2(const int16_t, const int16_t);

/* 9091 - 9025 */ 
#define DEFAULT_BAUD_RATE 9121
#define DEFAULT_SAMPLE_RATE 2400000

/* complete guess work for sane numbers */
#define MIN_SAMPLE_RATE 30000
#define MAX_SAMPLE_RATE 20000000

#define MAX_SIG INT8_MAX

int32_t max_sample=0;

/* defaults */
int unsigned_input = 1;
int invert_data = 0;
int baud_rate = DEFAULT_BAUD_RATE;
int sample_rate = DEFAULT_SAMPLE_RATE;
int verbose=0;

int gain=1;

// (16 * 16384)
#define INPUT_BUF_SIZE           1024 

struct IQ {
    int8_t     i;
    int8_t     q;
};

/* these are random valuses that seems to work */
int sample_threshold_low = (INPUT_BUF_SIZE / 1024 ) * 10 ;
int sample_threshold_hi =  (INPUT_BUF_SIZE / 1024 ) * 100 ;
uint8_t carrierThreshold = 10;
int phase_count = 2;

int sample_per_ms; //  = sample_rate / 1000;
/* 
float single_mark_ms    = 1/ ( 9124 / 1000.0 )
*/

// = 0.109597232079488;

float single_mark_ms    = 0.109599;
float single_mark_f=0.0;
int single_mark=0;
int stateMark=0;
int resync_cnt = 0;
int bit_count;	// output bit count
int byte_count; // bytes demodulated

char data_one='1';
char data_zero='0';

char *progname;

int debug=2;

void print_help(char *prog_name) {

    printf("%s [-b baud_rate] [-s sameple_rate] [-u|-U] [-i|-I] [-v] [-d] [-h]\n", prog_name);
    printf("Options :\n");
    printf("\t-b #\tbaudrate                (default=%d)\n", DEFAULT_BAUD_RATE);
    printf("\t-s #\tsample freq             (default=%d)\n", DEFAULT_SAMPLE_RATE);
    printf("\t-u  \tunsigned data           (default=%s)\n", "True");
    printf("\t-U  \tsigned data\n");
    printf("\t-i  \tinvert data             (default=%s)\n", "True");
    printf("\t-I  \tno invert\n");
    printf("\t-b #\tphase_count             (default=%d)\n", phase_count);

    printf("\t-t #\tsquelch level threshold (default=%d)\n", carrierThreshold );
    printf("\t-T #\tsquelch level count     (default=%hhd)\n", sample_threshold_hi);

    printf("\t-h  \tprint help\n");
    printf("\n");

}

void chk_val(int val, int minv, int maxv, char *name) {
    if ( val < minv || val > maxv ) {
	fprintf( stderr, "Invalid value for %s : %d\n", name, val);
	fprintf( stderr, "\tmin = %d\tmax = %d\n", minv, maxv);
	print_help(progname);
        exit(0);
    }
}

void init(int ac, char *av[] ) {
int ch; 
extern char *optarg;
extern int optind, opterr, optopt;

    // printf( "PRE : sample_threshold = %d : %d\n", sample_threshold_hi, sample_threshold_low );
    // printf( "PRE : carrierThreshold  = %d\n",  carrierThreshold );

    while ((ch = getopt(ac, av, "g:b:s:t:T:uUiIvdhp:")) != -1) {
        float f, g;
        // char *subopts, *value;
        switch (ch) {
            case 's' :
                sample_rate = atoi(optarg);
                break;
            case 'p' :
               phase_count = atoi(optarg);
               break;
            case 'b' :
               baud_rate = atoi(optarg);
               break;
            case 'u' :
               unsigned_input=1;
               break;
            case 'U' :
               unsigned_input=0;
               break;
            case 'i' :
               invert_data=1;
               break;
            case 'I' :
               invert_data=0;
               break;
            case 'T' :
               g = strtof(optarg, NULL);
	       f = ( g / 100.0 );
	       sample_threshold_hi = (int)  (INPUT_BUF_SIZE * f );
	       sample_threshold_low = sample_threshold_hi / 10 ;
               break;
            case 't' :
	       carrierThreshold = atoi(optarg);
               break;
            case 'g' :
                gain = atoi(optarg);
                break;
            case 'v' :
               verbose++;
               break;
            case 'd' :
               debug++;
               break;
            case 'h' :
               print_help(progname);
	       exit(0);
               break;
	}
    }


    // printf("POST: sample_threshold = %d : %d\n", sample_threshold_hi, sample_threshold_low );
    // printf( "POST : carrierThreshold  = %d\n",  carrierThreshold );

    if ( invert_data ) {
	data_one='0';
	data_zero='1';
    }
    sample_per_ms = sample_rate / 1000;
    single_mark_ms = 1/ ( baud_rate / 1000.0 );
    // single_mark = (int) (single_mark_ms * sample_per_ms);
    single_mark = (int) ( sample_rate/ baud_rate);
    single_mark_f = (float) ( sample_rate/ (float) baud_rate);


    // printf( "POST : single_mark  = %d\n",  single_mark );

    /*
       some of these limits are made up guesses
       the goal it to keep them in a sane range 
    */
    chk_val(sample_rate,
		( MIN_SAMPLE_RATE > (baud_rate * 8) ? MIN_SAMPLE_RATE : (baud_rate * 8) ),
		MAX_SAMPLE_RATE, "Sample Rate");
    chk_val(sample_threshold_hi, 2, ( INPUT_BUF_SIZE / 2 ), "Squelch Level Count");
    chk_val(carrierThreshold, 1, MAX_SIG, "Squelch Threshold");
    chk_val(phase_count, 1, 100, "Phase Sample Count");
    chk_val(baud_rate, 15, ( sample_rate / 8 ), "Baud Rate");

    // exit(0);

}

int resync_shift(struct IQ *iq, int loc, int pkt_offset, int ph) {
int x, y;
char i, q;
uint16_t ui;
uint16_t up;
int8_t prev_i;
int8_t prev_q;
int tp;


int x_start;


    x_start = loc - (pkt_offset *2) ;
    if (x_start < 0 ) {
	return -1;
    }
    prev_i =  iq[ loc ].i;
    prev_q =  iq[ loc ].q;
    up = fxpt_atan2( (int16_t)  prev_i,  (int16_t)  prev_q);
    for(x=loc; x > x_start; x--) {
	ui = fxpt_atan2( (int16_t)  iq[x].i, (int16_t)  iq[x].q);
	tp = up - ui;
	up = ui;

	if ( tp == 0 || tp > 32000 || tp < -32000 ) {
	    continue;
	}

	if ( (tp > 0 && ph > 0) || (tp < 0 && ph < 0) ) {
	    continue;
	} else {
	    return 0;
	}
    }


}

/* look fof first phase shift so we can sync with the data */
int find_shift(struct IQ *iq, int start, int len) {
int i;
int phase=0;
int prev_phase=0;

    for(i=start; i<len; i++) {

	/* look for I drop though 0 */
	if (iq[i].i >= 0 && iq[i+1].i < 0 ) {
	    if (iq[i].q > 0 ) {
		phase = 1;
	    } else {
		phase = -1;
	    }


	    if (prev_phase == 0) {
		prev_phase = phase;
	    } else if ( prev_phase != phase ) {
		return i;
	    }
	}
    }

    return 0;
}

void fsk(char *data, int data_len) {
int i=0;
int start_offset;
struct IQ *iq;
int iq_len;
uint16_t ui;
uint16_t up;
int phased=0;
static int stateMark_add=0;
static int stateMark_val=0;
static int stateMark_cnt=0;
static int stateMark_score=0;
static int8_t prev_i;
static int8_t prev_q;
    
int m;

    iq = (struct IQ *) data;
    iq_len = data_len / sizeof(struct IQ);
    start_offset=0;

    // if byte_count is 0 this is the first buffer 
    if (byte_count == 0 ) {
	

	i=0;
	
	for(i=0; i<iq_len; i++) { 
	    if  (iq[i].i > 10 )
	    break;
	}

	start_offset=i;
	i = find_shift(iq, i, data_len);
	// printf("# find shift = %d\n", i);
	stateMark = (i + (single_mark/2)) % single_mark ;
	// fprintf (stderr, "# stateMark  %d\n", stateMark);
	


	// stateMark = single_mark/2;

	if ( verbose > 1 ) {
	    fprintf (stderr, "#iq_len  %d\n", iq_len);
	    fprintf (stderr, "#start at %d\n", start_offset);
	    fprintf (stderr, "# stateMark  %d\n", stateMark);
	    fprintf (stderr, "# single_mark  %d\n", single_mark);
	} 
	byte_count = start_offset;

	prev_i = iq[start_offset].i;
	prev_q = iq[start_offset].q;
	// putchar('\n');
    }

    for(i=start_offset; i<iq_len; i++) {
	float fl;


	fl = (float) fmodf((float)byte_count, single_mark_f);
	// if ( (byte_count % single_mark) == stateMark )
	if ( stateMark == (int) fl ) 
	{
	    stateMark_add = 1;
	}
	byte_count++;


	if ( stateMark_add ) {
	    int tp;



	     /*
		check phase by waiting and calc phased
	    */
	    up = fxpt_atan2( (int16_t)  prev_i,  (int16_t)  prev_q);
	    ui = fxpt_atan2( (int16_t)  iq[i].i, (int16_t)  iq[i].q);
	    tp = ui - up;

	    /* avoid transitions */
	    if ( tp != 0 && tp < 32000 && tp > -32000 )
		phased=tp;

	    if ( resync_cnt > 10 ) {
		resync_cnt=0;
		resync_shift(iq, i, stateMark, phased) ;
	    } else {
		resync_cnt++;
	    }

	    if (phased > 0 ) {
		stateMark_score++;
		stateMark_cnt++;
	    } else if ( phased < 0 ) {
		stateMark_score--;
		stateMark_cnt++;
	    }

	    if ( stateMark_cnt >= phase_count ) {
		char data_val='?';
		if (stateMark_score < 0 ) {
		    data_val = data_zero;
		    stateMark_val=1;
		} else if (stateMark_score > 0 ) {
		    data_val = data_one;
		    stateMark_val=-1;
		}


		if ( data_val == '?' ) {
                    // printf("# %d %d data ??\n", byte_count, bit_count);
		} else {
		    bit_count++;
		    putchar(data_val);
		    stateMark_add = 0;
		    stateMark_cnt=0;
			stateMark_score=0;
		    }
		}

	    }

	stateMark_val=0;

	prev_i = iq[i].i;
	prev_q = iq[i].q;
    }
}

int  main(int ac, char *av[]) {
unsigned char buff[INPUT_BUF_SIZE];
// unsigned char buff[65536];
int i, j;
unsigned int k;
int b, c;
int carrier_detect=0;

    progname = av[0];
    setvbuf (stdout, NULL, _IONBF, BUFSIZ);
    setvbuf (stderr, NULL, _IONBF, BUFSIZ);

    init(ac, av);

    if ( verbose  ) {
	fprintf (stderr, "# invert  %d\n", invert_data);
	fprintf (stderr, "# baud  %d\n", baud_rate);
	fprintf (stderr, "# sample_rate  %d\n", sample_rate);
	fprintf (stderr, "# single_mark_ms  %f\n", single_mark_ms);
	fprintf (stderr, "# single_mark  %d\n", single_mark);
	fprintf (stderr, "# carrierThreshold  %d\n", carrierThreshold);
	fprintf (stderr, "# sample_threshold_low  %d\n", sample_threshold_low);
	fprintf (stderr, "# sample_threshold_hi  %d\n", sample_threshold_hi);
	fprintf (stderr, "# data_one  = %c \n", data_one);
	fprintf (stderr, "# data_zero = %c \n", data_zero);
    }

    fflush(stdout);
    fflush(stderr);

    b = 0;
    c = 0;
    while ( (i = read(0, buff, sizeof buff)) > 0) {
	k = 0;
	c++;

	for(j=0;j<i;j+=2) {
	    if ( unsigned_input ) {
		buff[j]   = buff[j]   - 127;
		buff[j+1] = buff[j+1] - 127;
	    }

//	    if ( (signed char) buff[j] > max_sample )
//		max_sample = (signed char) buff[j];

	    if ( gain > 1 ) {
		buff[j]   = buff[j]   * gain;
		buff[j+1] = buff[j+1] * gain;
	    }

	    if ( carrierThreshold < (signed char) buff[j] ) {
		k++;
	    }
	}


	if ( k > 100 ) {
	    if (carrier_detect == 0) {

		carrier_detect = 1;

		if ( verbose > 1) {
		    fprintf(stderr,"# %d: k = %d : %d\n", c, k, ( c * sizeof(buff) ) );
		}

		bit_count=0;  // reset 
		byte_count=0; // reset 
	    }
	} else if ( k < 10 ) {
	    if (carrier_detect == 1) {

		/*
		    2 means process buffer then
		    set to zero after next demod 
		*/
		carrier_detect=2;

		stateMark=0; // reset marker to check state
		putchar('\n');
		if ( verbose ) {
		    //  fprintf(stderr, "# drop:  %d: k = %d\n", c, k);
			fprintf(stderr, "# bit_count %d\n", bit_count);
		    fprintf(stderr, "# samples %d %0.2f ms\n", byte_count, (byte_count/(float) sample_per_ms) );
		}
		fflush(stdout);
		fflush(stderr);
	    }
	}

	if ( carrier_detect ) {
	    fsk((char *) buff, i);
	    if (carrier_detect == 2) {
		carrier_detect=0;
		fflush(stdout);
		byte_count=0; // reset 
	    }
	} else {
	    if ( b >= 1073741824 ) {
	    	b=0;
	    }
	}

	b++;
    } /* while read */

    if (carrier_detect ) {
	putchar('\n');
// fprintf(stderr, "#= max_sample %d\n", max_sample);
// max_sample=0;
	if ( verbose ) {
	    fprintf(stderr, "# bit_count %d\n", bit_count);
	    fprintf(stderr, "# buffering %d\n", c);
	    fprintf(stderr, "# samples %d %0.2f ms\n", byte_count, (byte_count/(float) sample_per_ms) );
	}
	fflush(stdout);
    }

    exit(0);
}



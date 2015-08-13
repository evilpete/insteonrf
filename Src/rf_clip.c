char static_string[]="Author Peter Shipley   2015\n";
/* 

	A simple program for reading 8 bit unsigned I/Q data
	into individual time stamped files

	This is Junk code written for (mostly) onetime use for proof of concept

*/

#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <limits.h>
#include <stdint.h>

#include<stdio.h>
#include<string.h>

#include <time.h>

#include <signal.h>

#define DEFAULT_SAMPLE_RATE 2400000
#define INPUT_BUF_SIZE           1024

int high_thr=(INPUT_BUF_SIZE / 1024 ) * 10 ;
int low_thr=(INPUT_BUF_SIZE / 1024 ) * 100 ;

// INT8_MAX / 12
int level_thr=10;

int sample_rate = DEFAULT_SAMPLE_RATE;

char *progname;

int samp_ms = DEFAULT_SAMPLE_RATE / 1000;

void sig_handler(int);

int unsigned_input=1;
int gain=1;

char nfilename[PATH_MAX + 1];


int timeout=0;
int squ_timeout=0;
int debug=1;
int verbose=0;

void print_help(char *prog_name) {


    printf("%s [-s sameple_rate] [-u|-U] [-i|-I] [-v] [-d] [-h]\n", prog_name);
    printf("Options :\n");
    printf("\t-s #\tsample freq             (default=%d)\n", DEFAULT_SAMPLE_RATE);
    printf("\t-u  \tunsigned data           (default=%s)\n", "True");
    printf("\t-U  \tsigned data\n");
    printf("\t-g  \tgain\n");

    printf("\t-l #\tsquelch hold (in ms)\n");

    printf("\t-t #\tsquelch level threshold (default=%d)\n", level_thr );
    printf("\t-T #\tsquelch level count     (default=%d)\n", high_thr);

    printf("\t-h  \tprint help\n");
    printf("\n");

}

int new_file(buf_count) {
int nfd;
char text[100];
time_t now = time(NULL);
struct tm *t = localtime(&now);


    strftime(text, sizeof(text)-1, "%d%m%Y-%H:%M:%S", t);
    snprintf(nfilename, sizeof(nfilename), "rf-%s-%04d.dat", text, buf_count);
    // printf("Next File : %s\n", nfilename);
    // fflush(stdout);

    nfd = open(nfilename, O_CREAT | O_WRONLY, 0664);
    if(nfd == -1){
	printf("Error creating file : %s\n", nfilename);
	perror("open");
    }

    return nfd;

}

int clips_max;
int clip_count;
char  max_value;
int buf_reads;



void init(int ac, char *av[] ) {
int ch; 
extern char *optarg;
extern int optind, opterr, optopt;


    progname = av[0];
    while ((ch = getopt(ac, av, "l:s:g:t:T:uUvdh")) != -1) {
        float f, g;
        // char *subopts, *value;
        switch (ch) {
            case 's' :
                sample_rate = atoi(optarg);
                break;
            case 'u' :
               unsigned_input=1;
               break;
            case 'U' :
               unsigned_input=0;
               break;
            case 'T' :
               g = strtof(optarg, NULL);
	       f = ( g / 100.0 );
	       high_thr = (int)  (INPUT_BUF_SIZE * f );
	       low_thr = high_thr / 10 ;
               break;
            case 'l' :
	       timeout = atoi(optarg);
               break;
            case 't' :
	       level_thr = atoi(optarg);
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

    int samp_ms = sample_rate / 1000;
    squ_timeout = timeout * samp_ms;

    // printf("timeout=%d squ_timeout=%d\n", timeout, squ_timeout);


    return ;
}




int main(int ac, char *av[]) {
unsigned char buff[INPUT_BUF_SIZE];
// char buff[65536];
int ofd = -1;
int i, j, k;
int b, c, ob, cb;
int lb; // last byte

    init(ac, av);

    if (ac > 1 && av[1][0] == '-' ) {
	char *p;
	p = av[1];
	p++;
	clips_max=atoi(p);
    }


    printf("RF Clip Started (clips_max=%d)\n", clips_max);
    printf("Thr Lo=%d Hi=%d : Lev=%d\n", low_thr,  high_thr, level_thr);


    signal(SIGINT, sig_handler);

    cb = 0;
    ob = 0;
    b = 0;
    c = 0;
    while ( (i = read(0, buff, sizeof buff)) > 0) {
	max_value=0;
	buf_reads++;
	k = 0;
	for(j=0;j<i;j++) {
	    c++;
	    char d;

	    if (unsigned_input) {
		d = buff[j] - 127;
		buff[j] = d;
	    } else {
		d = buff[j];
	    }

	    if (d > level_thr ) {
		k++;
	    }
	    if (d > max_value) {
		max_value = d;
	    }

	}
	fprintf(stderr,"%d: %d k = %d\n", c, b,  k);
	if ( k > high_thr ) {
	    lb = b;
	    if (ofd == -1) {
		int sm;
		ofd = new_file(b);
		sm = ((b -cb) * sizeof(buff))/2;
		ob=b;
		printf("# start %d %0.2f ms (max val=%d)\n", sm, (sm/ (float) samp_ms), max_value );
		// max_value=0;
		clip_count++;
		if ( debug )
		    fprintf(stderr,"Start k = %d\n", k);
	    }
	} else if ( k < low_thr ) {
	    if ( (ofd != -1) && ( (b - lb) > squ_timeout ) ) {
		int sm;
		write(ofd, buff, i);
		close(ofd);
		cb=b;
		sm = ((b -ob) * sizeof(buff))/2;
		printf("# end  %d %0.2f ms (max val=%d)\n", sm, (sm/ (float) samp_ms), max_value );
		// max_value=0;
		ofd = -1;
		puts(nfilename);
		memset(nfilename, 0, sizeof(nfilename));
		if ( debug )
		    fprintf(stderr,"End k = %d\n", k);
		fflush(stdout);
	    }
	}
	if ( ofd > -1 ) {
	    write(ofd, buff, i);
	} else {
	    // 2^30 = 1073741824
	    if ( b >= 1073741824 ) {
	    	b=0;
	    }
	    if ( clips_max > 1 &&  clip_count >= clips_max ) {
		printf("# Max clip written %ds\n", clip_count );
		break;
	    }
	}
	b++;
    }

    exit(0);
}

void sig_handler(int sig) {
    switch (sig) {
    case SIGINT:
        fprintf(stderr, "max_value=%d\n", max_value);
        fprintf(stderr, "buf_reads=%d\n", buf_reads);
	exit(0);
    default:
        fprintf(stderr, "wasn't expecting that! ( sig=%d)\n", sig);
        fprintf(stderr, "max_value=%d\n", max_value);
        fprintf(stderr, "buf_reads=%d\n", buf_reads);
	exit(0);
    }
}

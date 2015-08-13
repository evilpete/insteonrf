
#include<stdint.h>


#ifndef IQSAMPLESIZE
#warning "IQSAMPLESIZE not set, assuming 16bit"
#define IQSAMPLESIZE 8
#endif


#if IQSAMPLESIZE != 8 && IQSAMPLESIZE != 16 
#error "IQSAMPLESIZE must be set to the value 8 or 16"
#endif

struct wavfile
{
    char        id[4];          // should always contain "RIFF"
    int     totallength;    // total file length minus 8
    char        wavefmt[8];     // should be "WAVEfmt "
    int     format;         // 16 for PCM format
    short     pcm;            // 1 for PCM format
    short     channels;       // channels
    int     frequency;      // sampling frequency
    int     bytes_per_second;
    short     bytes_by_capture;
    short     bits_per_sample;
    char        data[4];        // should always contain "data"
    int     bytes_in_data;
};

struct subChunk {
    char        id[4];          // should always contain "RIFF"
    int     len;    // total file length minus 8
};

struct IQ_8 {
    int8_t     i_val;
    int8_t     q_val;
};


struct IQ_16 {
    short     i_val;
    short     q_val;
};

#if IQSAMPLESIZE == 8 
typedef struct IQ_8	IQ_t;
#elif IQSAMPLESIZE == 16
typedef struct IQ_16	IQ_t;
#endif



struct IQState {
    int zero_pass_up;
    int zero_pass_down;
    int peak;
    int valley;
};

struct clipinfo {
    int 	start;
    int 	end;
    short 	max;
    short	avg;	
} ;

struct timeline_pt {
    int		i;
    int		len;
    int 	state;
};

#define member_size(type, member) sizeof(((type *)0)->member)

void smooth_dat_2();
void smooth_dat_9();
struct clipinfo *findclips();
void *find_chunk();

int getwavdata();

int     roundUp(int, int) ;
int8_t  *scale16to8(int16_t *, int8_t *, int);
float   _Complex *scale8tocomplex(int8_t *, float _Complex *, int);
int16_t *scale8to16(int8_t *, int16_t *, int);
float   *scale8tofloat(int8_t *, float *, int); 
int8_t  *scalefloatto8(float *, int8_t *, int);


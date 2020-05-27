
UNAME = `uname`

CC=gcc

# ifeq ($(UNAME),Linux)
# CC=gcc-4.7
# endif

# .if ${UNAME}=="FreeBSD"
# CC=gcc47
# .endif

# ifeq ($(UNAME),FreeBSD)
# CC=gcc47
# endif

MKDIR_P = mkdir -p

OBJECTS_DIR=Obj
SOURCE_DIR=Src
CFLAGS+=-ggdb -O2 -Wall
LDFLAGS+=-ggdb
LINTFLAGS=-g -n -u -z
TESTWAV=Dat/41802513110D2711018C00.dat


all: directories  fsk2_demod rf_clip
	if [ -d "MStar_lock" ]; then ( cd "MStar_lock" ; make );  fi



.PHONY: directories

directories: ${OBJECTS_DIR} ${SOURCE_DIR}

${OUT_DIR}:
	${MKDIR_P} ${OUT_DIR}

fsk2_mod: $(OBJECTS_DIR)/fsk2_mod.o 
	$(CC) $(LDFLAGS) -O2 -pipe $+ -o $@ -lm -lliquid

# fsk2_demod: $(OBJECTS_DIR)/fsk2_demod.o $(OBJECTS_DIR)/fxpt_atan2.o
# 	$(CC) $(LDFLAGS) -O2 -pipe $+ -o $@ -lm
##	$(CC) $(LDFLAGS) -O2 -pipe $< $(OBJECTS_DIR)/fxpt_atan2.o -o $@ -lm

rf_clip:  $(OBJECTS_DIR)/rf_clip.o
	$(CC) $(LDFLAGS) -O2 -pipe $< -o $@


########## 8 bit

$(OBJECTS_DIR)/rf_clip.o: ${SOURCE_DIR}/rf_clip.c
	$(CC) -g  -c $(CFLAGS) -o $@ $<

$(OBJECTS_DIR)/fxpt_atan2.o: ${SOURCE_DIR}/fxpt_atan2.c
	$(CC) -g -c $(CFLAGS) -o $@ $<

$(OBJECTS_DIR)/fsk2_mod.o: ${SOURCE_DIR}/fsk2_mod.c
	$(CC) -g  -c $(CFLAGS) -o $@ $< -I/usr/local/include/liquid 

$(OBJECTS_DIR)/fsk2_demod.o: ${SOURCE_DIR}/fsk2_demod.c
	$(CC) -g  -c $(CFLAGS) -o $@ $<

##########

$(OBJECTS_DIR)/insteon_lib.o: ${SOURCE_DIR}/insteon_lib.c
	$(CC) -g -c $(CFLAGS) -o $@ $<

$(OBJECTS_DIR)/convert.o: ${SOURCE_DIR}/convert.c
	$(CC) -g -c $(CFLAGS) -o $@ $<

$(OBJECTS_DIR)/convert_lib.o: ${SOURCE_DIR}/convert_lib.c
	$(CC) -g -c $(CFLAGS) -o $@ $<

convert: $(OBJECTS_DIR)/convert.o $(OBJECTS_DIR)/convert_lib.o 
	$(CC) $(LDFLAGS) -O2 -pipe $^ -o $@

insteon_pkt_crc: insteon_pkt_crc.o $(OBJECTS_DIR)/insteon_lib.o 
	$(CC) $(LDFLAGS) -O2 -pipe $^ -o $@


$(OBJECTS_DIR):
	@mkdir $(OBJECTS_DIR)

lint:
	@lint $(LINTFLAGS) ${SOURCE_DIR}/fsk2_demod.c
	@lint $(LINTFLAGS) ${SOURCE_DIR}/rf_clip.c
	@lint $(LINTFLAGS) ${SOURCE_DIR}/fsk2_mod.c
	@lint $(LINTFLAGS) ${SOURCE_DIR}/convert.c
	@lint $(LINTFLAGS) ${SOURCE_DIR}/conver_lib.c


p:
	echo UNAME ${UNAME}
	echo OSTYPE ${OSTYPE}
	echo CC ${CC}

clean:
	@/bin/rm -rf $(OBJECTS_DIR)

realclean:
	@/bin/rm -rf $(OBJECTS_DIR)
	@/bin/rm -f ./rf_clip ./fsk2_demod ./fsk2_mod

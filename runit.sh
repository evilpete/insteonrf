#!/bin/sh

# <this_script>  | python print_pkt.py 



# sample rates
# valid  : 250000 1000000 1024000 1800000 1920000 2000000 2048000 2400000 
# not so valid :  2600000 2800000 3000000 3200000

bindir="/usr/local/bin"
# freq=914975000
freq=914950000

samprate=2400000
rfgain=1



while /bin/true ; do
    ${bindir}/rtl_sdr -g ${rfgain} -f ${freq} -s ${samprate} - | ./fsk_demod 
    # -v -d
done



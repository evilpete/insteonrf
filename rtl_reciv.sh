#!/bin/sh
# This script recieves input from rtl_sdr and outputs it to stdout
# To debug packets:
# <this_script>  | python print_pkt.py 

rtlsdr_path=$(which rtl_sdr)
if [[ $? != 0 ]]; then
    echo "Could not find rtl_sdr in path."
    exit 1
fi

freq=914950000
samprate=2400000
rfgain=19.9

writeblksize=65536

while true ; do
    rtl_sdr -g ${rfgain} -f ${freq} -s ${samprate} -b ${writeblksize} -
    ret=$?
    echo "rtl_sdr exit code : ${ret}" >&2
    # -v -d
done

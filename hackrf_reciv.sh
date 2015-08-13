#!/bin/sh

#
#        -t <filename> # Transmit data from file.
#        -w # Receive data into file with WAV header and automatic name.
#           # This is for SDR# compatibility and may not work with other software.
#        [-f freq_hz] # Frequency in Hz [0MHz to 7250MHz].
#        [-i if_freq_hz] # Intermediate Frequency (IF) in Hz [2150MHz to 2750MHz].
#        [-o lo_freq_hz] # Front-end Local Oscillator (LO) frequency in Hz [84MHz to 5400MHz].
#        [-m image_reject] # Image rejection filter selection, 0=bypass, 1=low pass, 2=high pass.
#        [-a amp_enable] # RX/TX RF amplifier 1=Enable, 0=Disable.
#        [-p antenna_enable] # Antenna port power, 1=Enable, 0=Disable.
#        [-l gain_db] # RX LNA (IF) gain, 0-40dB, 8dB steps
#        [-g gain_db] # RX VGA (baseband) gain, 0-62dB, 2dB steps
#        [-x gain_db] # TX VGA (IF) gain, 0-47dB, 1dB steps
#        [-s sample_rate_hz] # Sample rate in Hz (8/10/12.5/16/20MHz, default 10MHz).
#        [-n num_samples] # Number of samples to transfer (default is unlimited).
#        [-c amplitude] # CW signal source mode, amplitude 0-127 (DC value to DAC).
#        [-b baseband_filter_bw_hz] # Set baseband filter bandwidth in MHz.
#        Possible values: 1.75/2.5/3.5/5/5.5/6/7/8/9/10/12/14/15/20/24/28MHz, default < sample_rate_hz.
#
# eg:
#



#


thedate=`date +%Y%m%d-%H%M%S`

# 5sec
sample_num=6000000
baseband_f=2200000 



# freq=914975000
freq=914950000
#freq=914973000
#sample_rate=2048000
sample_rate=2400000
#sample_rate=1750000

filen=hackrf-${thedate}-${freq}

# echo "File : " ${filen}

#hf_transfer=hackrf_transfer 
hf_transfer=/mnt/alix2/SDR/Insteon/HRF/hackrf/host/build/hackrf-tools/src/hackrf_transfer


$hf_transfer -l 16 -g 8 -a 1 -s ${sample_rate} -f ${freq} -r -


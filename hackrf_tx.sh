#!/bin/sh

# requires a modified version of hackrf_transfer that reads from stdin


freq=914950000
# freq=914973000
sample_rate=2400000


#this generated sample fails to transmit
# dat_file="garage_on.dat"
 
# this recored sameple works
# dat_file="rf-garage_on.dat"


hackrf_transfer -x 20 -a 1 -s ${sample_rate} -f ${freq} -t -


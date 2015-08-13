#!/bin/sh


freq=914950000
#freq=914973000
sample_rate=2400000

rm -f /tmp/hrf.$$

cat > /tmp/hrf.$$

ls -ls /tmp/hrf.$$

#this generated sample fails to transmit
dat_file="garage_on.dat"
 
# this recored sameple works
# dat_file="rf-garage_on.dat"


hackrf_transfer -x 20 -a 1 -s ${sample_rate} -f ${freq} -t /tmp/hrf.$$


rm /tmp/hrf.$$

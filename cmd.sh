sudo pptpsetup --create test2 --server 77.73.67.86 --username pptp --password ttTArkzpc7p9 --start --encrypt

#!/bin/bash
connect
DI=`route -n | egrep -v UGH | grep UG | awk '{print $8}'`
DGW=`route -n | grep $DI | head -n 1 | awk '{print $2}'`
VPNI=`route -n | egrep -v UGH | grep UH | awk '{print $8}'`
VPNGW=`route -n | grep $VPNI | head -n 1 | awk '{print $1}'`

echo DI: $DI
echo DGW: $DGW
echo VPNI: $VPNI
echo VPNGW: $VPNGW

route add default gw $VPNGW  dev $VPNI
route del default gw $DGW dev $DI


#!/bin/bash
disconnect
VPNI=`route -n | egrep -v UGH | grep UG | awk '{print $8}'`
VPNGW=`route -n | grep $VPNI | head -n 1 | awk '{print $2}'`
DI=`route -n | grep UGH | awk '{print $8}'`
DGW=`route -n | grep $DI | head -n 1 | awk '{print $2}'`

echo DI: $DI
echo DGW: $DGW
echo VPNI: $VPNI
echo VPNGW: $VPNGW

route add default gw $DGW dev $DI
route del default gw $VPNGW dev $VPNI

killall pppd
#!/bin/bash



count=$( ping -c 1 google.com | grep icmp* | wc -l )
while true; do

	if [ $count -eq 0 ]
	then

		date		
		espeak 'wifi down'		
		echo "Reset Wifi..."
		nmcli d disconnect iface wlan0
		sleep 1
		nmcli c up id '@ AISwifi'
		sleep 15

	#else
	#	echo "Yes! Host is Alive!"

	fi
sleep 3
done


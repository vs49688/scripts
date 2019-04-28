#!/bin/sh -e
##
# Utility script to handle connecting the controller from MEDIA
# to CAPRICA.
#
# bind/unbind should be run on MEDIA
# attach/detach should be run on CAPRICA
##

SERVER=192.168.0.165
USBIP=/usr/bin/usbip

if [ $# -ne 1 ]; then
	echo "Usage: $0 <bind|unbind|attach|detach>"
	exit 2
fi

if [ $1 = "bind" ] || [ $1 = "unbind" ]; then
	modprobe usbip_host
	BUSID=$(${USBIP} list -p -l | sed -nr 's/^busid=(.+)#usbid=045e:028e#$/\1/p')
elif [ $1 = "attach" ]; then
	modprobe vhci-hcd
	BUSID=$(${USBIP} list -r ${SERVER} | sed -nr 's/^\s*([0-9]+-[0-9]+):.+\(045e:028e\)\s*$/\1/p')
elif [ $1 = "detach" ]; then
	modprobe vhci-hcd
	# Technically the "port" id
	BUSID=$(${USBIP} port | grep -B1 045e:028e | head -1 | sed -nr 's/^Port\s+([0-9]+).+$/\1/p')
else
	echo "Usage: $0 <bind|unbind|attach|detach>"
	exit 2
fi

if [ -z ${BUSID} ]; then
	echo "Unable to locate controller, exiting..."
	exit 1
fi

if [ $1 = "bind" ]; then
	${USBIP} bind -b ${BUSID}
elif [ $1 = "unbind" ]; then
	${USBIP} unbind -b ${BUSID}
elif [ $1 = "attach" ]; then
	${USBIP} attach -r ${SERVER} -b ${BUSID}
elif [ $1 = "detach" ]; then
	${USBIP} detach -p ${BUSID}
fi

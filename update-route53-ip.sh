#!/bin/sh -e

if [ $# -ne 2 ]; then
	echo "Usage: $0 <zone_id> <record_name>"
	exit 2
fi

HOSTED_ZONE_ID=$1
RECORD_NAME=$2

# Always assign these to a variable so the exit status is preserved
# See https://superuser.com/a/363454

set +e

WAN_IP=""
for i in \
	"dig @resolver1.opendns.com ANY myip.opendns.com +short" \
	"dig @ns1-1.akamaitech.net ANY whoami.akamai.net +short" \
	"dig @ns1.google.com TXT o-o.myaddr.l.google.com +short"; do
	WAN_IP=$($i)
	if [ $? -eq 0 ]; then
		break
	fi 
done

if [ -z ${WAN_IP} ]; then
	echo "Unable to query WAN IP, exiting..."
	exit 1
fi

set -e

HOSTNAME=$(hostname)
TIMESTAMP=$(date -Iseconds)

exec aws route53 change-resource-record-sets \
	--hosted-zone-id ${HOSTED_ZONE_ID} \
	--change-batch file:///dev/stdin <<EOF
{
	"Comment": "Update from ${HOSTNAME} at ${TIMESTAMP}",
	"Changes": [
		{
			"Action": "UPSERT",
			"ResourceRecordSet": {
				"Name": "${RECORD_NAME}",
				"Type": "A",
				"TTL": 3600,
				"ResourceRecords": [{ "Value": "${WAN_IP}" }]
			}
		}
	]
}
EOF

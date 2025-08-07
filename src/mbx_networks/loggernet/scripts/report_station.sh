#!/bin/bash

trap 'rm -f "$TMPFILE"' EXIT

TMPFILE=$(mktemp --suffix .json) || exit 1
# echo "Our temp file is $TMPFILE"

## Get a station's data
cora_cmd \
--echo=on \
--input="{
connect localhost; 
logger-query-ex ${1} FiveMin $TMPFILE most-recent 3 --format=\"CSIXML\" --reported-station-name=${1};
}"

sleep 0.1

cat $TMPFILE |
	xq . |
       tee $TMPFILE > /dev/null

#cat $TMPFILE

curl -X POST -d @$TMPFILE --header "loggernet: push" --header "station: ${1}" https://mesonet.climate.umt.edu/api/v2/loggernet/
curl -X POST -d @$TMPFILE --header "loggernet: push" --header "station: ${1}" https://fcfc-mesonet-staging.cfc.umt.edu/api/v2/loggernet/
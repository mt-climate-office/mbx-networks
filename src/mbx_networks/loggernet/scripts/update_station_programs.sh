#!/bin/bash

stations="`curl https://mesonet.climate.umt.edu/api/v2/loggernet/ | jq -r '. | @sh' | tr -d \'`"

echo $stations

for station in $stations
do
    timeout 2m /opt/update_station_program.sh $station
done
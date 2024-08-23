#!/bin/bash

cora_cmd \
--echo=off \
--input='{
connect localhost;
create-backup-script /opt/mesonet-ln-server/network_config.cora;
}'
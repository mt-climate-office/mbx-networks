#/bin/bash

# Install loggernet
RUN dpkg --install /opt/$(basename $LN_LINUX)
ln -s /opt/CampbellSci/LoggerNet/cora_cmd /usr/local/bin/cora_cmd
/etc/init.d/csilgrnet start

tail -f /dev/null
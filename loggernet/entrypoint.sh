#!/bin/sh
set -e -x -v

echo "Downloading ln software"
# Define the SSH command
GIT_SSH_COMMAND='ssh -i /run/secrets/SSH_KEY'

# Function to clone or pull a repository
clone_or_pull() {
    local repo_url=$1
    local clone_dir=$2

    if [ -d "$clone_dir" ]; then
        echo "Directory $clone_dir exists. Performing git pull."
        GIT_SSH_COMMAND="$GIT_SSH_COMMAND" git -C "$clone_dir" pull
    else
        echo "Directory $clone_dir does not exist. Performing git clone."
        GIT_SSH_COMMAND="$GIT_SSH_COMMAND" git clone "$repo_url" "$clone_dir"
    fi
}

# Repositories and their target directories
clone_or_pull "git@github.com:mt-climate-office/mesonet-ln-software" "/opt/mesonet-ln-software"
clone_or_pull "git@github.com:mt-climate-office/mesonet-ln-server" "/opt/mesonet-ln-server"
clone_or_pull "git@github.com:mt-climate-office/mesonet-ln-programs" "/opt/mesonet-ln-programs"


printf '#!/bin/sh\nexit 0' > /usr/sbin/policy-rc.d

echo "Installing LoggerNet"
dpkg --install /opt/mesonet-ln-software/loggernet-debian_4.7-12_x86_64.deb

ln -s /opt/CampbellSci/LoggerNet/cora_cmd /usr/local/bin/cora_cmd
chmod u+x /opt/*.sh

export SSH_KEY=$(cat /run/secrets/SSH_KEY)

# Verify our environment variables are set
[ -z "${SSH_KEY}" ] && { echo "Need to set SSH_KEY"; exit 1; }

# Set up our SSH Key
echo "Configuring SSH Key"

echo "${SSH_KEY}" > ~/.ssh/id_rsa
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa

# Configure our user and email to commit as.
echo "Configuring git"
git config --global user.name "Git Service"
git config --global user.email git@example.com

echo "Starting LoggerNet Service"
/etc/init.d/csilgrnet start

## restore initial configuration
cd /opt/mesonet-ln-server
git pull
#bash /opt/restore_config.sh

sleep 30

env >> ~/env.log
echo 'PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' > /etc/crontab
echo 'SHELL=/bin/bash' >> /etc/crontab
echo '0 * * * * root bash -c "source $HOME/env.log; source /opt/backup_config.sh"' >> /etc/crontab # every hour, check for server config updates
echo '*/5 * * * * root bash -c "source $HOME/env.log; source /opt/update_stations.sh"' >> /etc/crontab # Every 5 minutes, check for new data
echo '*/15 * * * * root bash -c "source $HOME/env.log; source /opt/update_station_programs.sh"' >> /etc/crontab # Every 15 minutes, check for program updates

echo "Host *\n    StrictHostKeyChecking no\n    UserKnownHostsFile=/dev/null\n" > ~/.ssh/config

# start cron
service cron start
service rsyslog start

tail -f /dev/null

# FROM bitnami/minideb:buster
FROM python:3-slim-bullseye
# MAINTAINER Kyle Bocinsky, bocinsky@gmail.com

ENV SSH_KEY=""

EXPOSE 6789

# install dependencies
RUN apt-get update && apt-get install -y \
      curl \
      libcurl4 \
      zip \
      xdg-utils \
      htop \
      net-tools \
      openssh-client \
      git \
      cron \
      vim \
      rsyslog \
      jq

RUN pip install yq

## Set time zone for server
#ENV TZ=America/Denver
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Download public key for github.com
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

COPY entrypoint.sh /entrypoint.sh

# Multipath fix for docker VM
RUN echo '\
defaults {\n\
    user_friendly_names yes\n\
}\n\
blacklist {\n\
    devnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\
    devnode "^sd[a-z]?[0-9]*"\n\
}' | tee /etc/multipath.conf

ENTRYPOINT ["/entrypoint.sh"]

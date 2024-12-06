FROM python:3.12-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

EXPOSE 6789

# needed to run wine
RUN dpkg --add-architecture i386

# Tools needed to install wine
RUN apt-get update && apt-get install -y \
    wget \
    xvfb \
    coreutils \
    zip \
    xdg-utils \
    sudo

# install wine
RUN mkdir -pm755 /etc/apt/keyrings
RUN wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
RUN wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/bookworm/winehq-bookworm.sources
RUN apt install -y --install-recommends wine

# Install compile checker
COPY ./scripts/check_compile.sh /opt/check_compile
RUN chmod +x /opt/check_compile
RUN ln -s /opt/check_compile /usr/local/bin/check_compile

# Create wine user b/c it causes issues to run wine as root
RUN useradd -ms /bin/bash wine && \
    echo "wine ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN mkdir -p /opt/usr && chown -R wine:wine /opt/usr

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown wine:wine /entrypoint.sh

USER wine
ENTRYPOINT [ "/entrypoint.sh" ] 
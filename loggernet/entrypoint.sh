#!/bin/bash

sudo dpkg --install /opt/ln/$LN_VERSION
sudo ln -s /opt/CampbellSci/LoggerNet/cora_cmd /usr/local/bin/cora_cmd
sudo /etc/init.d/csilgrnet start

uv sync --frozen --no-cache

/app/.venv/bin/fastapi run app/main.py --port 8080 --host 0.0.0.0 --reload

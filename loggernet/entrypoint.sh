#!/bin/bash

sudo dpkg --install /opt/ln/$LN_VERSION
sudo ln -s /opt/CampbellSci/LoggerNet/cora_cmd /usr/local/bin/cora_cmd
sudo /etc/init.d/csilgrnet start


if [ "$APP_MODE" = "debug" ]; then
    echo "Debugging"
    sudo uv sync --frozen --no-cache
    /app/.venv/bin/python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
else
    echo "Not Debugging"
    sudo uv sync --frozen --no-cache --no-dev
    /app/.venv/bin/fastapi run app/main.py --port 8080 --host 0.0.0.0 --reload
fi
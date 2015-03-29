#!/bin/sh

# Activate virtual env if there is one
if [ -d "venv" ]; then
    . ./venv/bin/activate
fi

python imsearch_http_service.py {server_port}
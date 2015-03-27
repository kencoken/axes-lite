#!/bin/sh

ARGS="--log-level INFO"
if [ "{debug}" = "True" ]; then
    ARGS="--log-level DEBUG --debug"
fi

# CD to server folder
cd server

# Activate virtual env if there is one
if [ -d "venv" ]; then
    . ./venv/bin/activate
fi

# Setup environment
export AXESHOME_SETTINGS=$PWD/settings.cfg

# Run gunicorn
gunicorn axeshome:app $ARGS --bind :{server_port} -t 120 --log-file=-

cd $OLDPWD

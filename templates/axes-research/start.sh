#!/bin/sh

ARGS="--log-level INFO --env DJANGO_SETTINGS_MODULE=axesresearch.settings.production"
if [ "{debug}" = "True" ]; then
    ARGS="--log-level DEBUG --debug --env DJANGO_SETTINGS_MODULE=axesresearch.settings.dev"
fi

# Activate virtual env if there is one
if [ -d "venv" ]; then
    . ./venv/bin/activate
fi

# Run gunicorn
gunicorn axesresearch.wsgi --pythonpath . \
    -k gevent \
    --log-file=- \
    -t 120 \
    -b localhost:{server_port} $ARGS

cd $OLDPWD

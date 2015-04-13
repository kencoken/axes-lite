#!/bin/bash

if ! screen -list | grep axes-support; then
    screen -AdmS axes-support -t mongodb bash -lc "bash --init-file <(echo \"{mongo_path}/mongod --port {mongo_port} --dbpath {mongo_dbpath}\")"
    screen -S axes-support -X screen -t nginx bash -lc "bash --init-file <(echo \"{nginx_path}/sbin/nginx -c {nginx_config}\")"
else
    echo "    AXES-SUPPORT screen instance already started - reattach with '$ screen -r axes-support'"
fi

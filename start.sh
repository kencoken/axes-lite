#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Specify the frontend you wish to use: either axes-home or axes-research"
    exit 1
fi

if ! screen -list | grep axes-lite; then
    echo "Launching backend components..."
    screen -AdmS axes-lite -t cpuvisor-srv bash -lc "bash --init-file <(echo \"cd cpuvisor-srv; ./start.sh\")"
    screen -S axes-lite -X screen -t imsearch-tools bash -lc "bash --init-file <(echo \"cd imsearch-tools; ./start.sh\")"
    screen -S axes-lite -X screen -t limas bash -lc "bash --init-file <(echo \"cd limas; ./start.sh\")"

    echo -n "Launching frontend components..."
    seq 1 6 | while read i; do sleep 0.5; echo -n "."; done
    echo ""

    if [ "$1" == "axes-home" ]; then
        screen -S axes-lite -X screen -t axes-home bash -lc "bash --init-file <(echo \"cd axes-home; ./start.sh\")"
    elif [ "$1" == "axes-research" ]; then
        screen -S axes-lite -X screen -t axes-research bash -lc "bash --init-file <(echo \"cd axes-research; ./start.sh\")"
    else
        echo "Invalid frontend: $1"
        screen -S axes-lite -X quit
        exit 1
    fi

    echo "Attaching to screen..."
    screen -r axes-lite -p 0
else
    echo "    AXES-LITE screen instance already started - reattach with '$ screen -r axes-lite'"
fi

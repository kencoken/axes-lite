#!/bin/sh

# if an individual environment setup exists, source it.
if [ -f "setup_env.sh" ]; then
  source ./setup_env.sh
fi

cd bin
./cpuvisor_service --config_path ../config.{name}.prototxt

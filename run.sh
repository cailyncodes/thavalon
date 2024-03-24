#!/bin/sh
COMMAND=$1

# check if the first argument is start
if [ "$COMMAND" == "start" ]; then
    podman compose up -d
fi
if [ "$COMMAND" == "stop" ]; then
    podman compose down
fi

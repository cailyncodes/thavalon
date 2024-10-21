#!/bin/sh
COMMAND=$1

# check if the first argument is start
if [ "$COMMAND" == "start" ]; then
    docker-compose up -d
fi
if [ "$COMMAND" == "stop" ]; then
    docker-compose down
fi

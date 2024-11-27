#!/bin/sh
COMMAND=$1

if [ "$COMMAND" == "start" ]; then
    docker-compose up -d
fi
if [ "$COMMAND" == "stop" ]; then
    docker-compose down
fi
if [ "$COMMAND" == "test" ]; then
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml run --rm -it api test
fi
if [ "$COMMAND" == "compile-requirements" ]; then
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml run --rm -it api compile-requirements
fi

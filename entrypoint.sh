#!/bin/sh
COMMAND=$1

if [ "$COMMAND" = "test" ]; then
    export PYTHONPATH=api
    python -m unittest discover -s api/tests
fi
if [ "$COMMAND" = "compile-requirements" ]; then
    pip-compile api/requirements.in --output-file api/requirements.txt
fi

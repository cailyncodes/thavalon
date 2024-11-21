#!/bin/sh
pip install -r requirements.txt
sanic index:app --host 0.0.0.0 --workers 4 --dev

#!/bin/bash

gunicorn -c cloud_eval/gunicorn.conf.py --pid GUNICORN_PID_FILE server.main:app
sleep 10
python -m gaiaframework.base.cloud_eval.worker $1 $2
kill $(cat GUNICORN_PID_FILE)
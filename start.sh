#!/bin/bash

gunicorn -c "/src/deployment/wsgi/gunicorn.conf.py"

echo this thing is now running

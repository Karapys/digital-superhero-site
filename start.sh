#!/bin/sh
mv env .env
source .env
cd app
gunicorn -w 1 --bind 0.0.0.0:8080 --bind 0.0.0.0:3306 --log-level debug wsgi:app
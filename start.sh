#!/bin/sh
flask db migrate
flask db upgrade

cd app
gunicorn -w 4 --bind 0.0.0.0:8080 --log-level debug wsgi:app \
--timeout 200 \
--reload \
--preload
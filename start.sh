#!/bin/sh
mv env .env
source .env
cd app
celery worker -A app.celery --loglevel=DEBUG --concurrency=1 -E &
gunicorn -w 1 --bind 0.0.0.0:8080 --bind 0.0.0.0:3306 --log-level debug wsgi:app
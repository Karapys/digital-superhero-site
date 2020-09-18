#!/bin/sh

source .env

gunicorn -w 1 --bind 0.0.0.0:8080 --log-level debug wsgi:app
celery worker -A app.celery --loglevel=DEBUG --concurrency=1 -P gevent -E

from flask import Flask
from sqlalchemy.engine.url import URL as create_url
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from celery import Celery
import redis

import logging
import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.urandom(32)
ALLOWED_EXTENSIONS = {'jpg', "jpeg"}

redis_host = os.getenv('REDISHOST', 'localhost')
redis_port = int(os.getenv('REDISPORT', 6379))
redis_url = os.getenv('REDIS_URL', f"redis://{redis_host}:{redis_port}")
redis_client = redis.Redis(host=redis_host, port=redis_port)

app = Flask(__name__)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = "static"
app.config.update(
    CELERY_BROKER_URL=redis_url + "/0",
    CELERY_RESULT_BACKEND=redis_url + "/0",

    DEBUG=True
)

print(app.config['CELERY_BROKER_URL'])
celery = Celery(app.name, broker=redis_url + "/0", backend=redis_url + "/0")
# celery.conf.update(app.config)

db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]
db_ip, db_port = os.getenv("DB_HOST", "127.0.0.1:3306").split(":")

url = str(create_url(
    drivername="postgresql",
    username=db_user,
    password=db_pass,
    host=db_ip,
    port=db_port,
    database=db_name
))
print(url)
#url += "?ssl_key=ssl/client-key.pem&ssl_cert=ssl/client-cert.pem"
# ssl_args = {'connect_args': {'sslmode':'verify-ca',
#                              'sslrootcert':'ssl/server-ca.pem',
#                              'sslcert':'ssl/client-cert.pem',
#                              'sslkey':'ssl/client-key.pem'}}
#ssl_mode=verify-ca&ssl_root_cert=server-ca.pem&
#print(url)
app.config['SQLALCHEMY_DATABASE_URI'] = url

db = SQLAlchemy(app)
migrate = Migrate(app, db)


def get_status_of_files():
    status_of_files = redis_client.get("status_of_files")
    if status_of_files is None:
        return {}
    return pickle.loads(status_of_files)


def save_status_of_files(status_of_files):
    redis_client.set('status_of_files', pickle.dumps(status_of_files))


def change_status(filename, status_of_file):
    status_of_files = get_status_of_files()
    status_of_files[filename] = status_of_file
    save_status_of_files(status_of_files)


from celery.contrib import rdb
@celery.task
def process_file(path, filename):
    rdb.set_trace()
    print(path, filename)
    change_status(filename, "processing")
    # time.sleep(10)
    with open(path) as f:
        pass
    change_status(filename, "ready")


from app.views import *

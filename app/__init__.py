from flask import Flask
from sqlalchemy.engine.url import URL as create_url
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import os

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.config['SECRET_KEY'] = SECRET_KEY

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

from app.views import *

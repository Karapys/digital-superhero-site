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


url = create_url(
    drivername="postgress",
    username="username",
    password="passSsadas@",
    host="host",
    port=5432,
    database="db"
)
app.config['SQLALCHEMY_DATABASE_URI'] = url

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.views import *

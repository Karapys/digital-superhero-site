from app import app
from flask import render_template
from flask_login import LoginManager
from app.models import *


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def home():
    user = User.query.all().first()
    return render_template("index.html", user=user)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

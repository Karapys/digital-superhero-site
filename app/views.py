from app import app, celery, db, redis_client, process_file, get_status_of_files
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from app.utils import is_safe_url, get_extension_if_valid
from app.models import *
from os.path import join
from random import random
import pickle
import hashlib
import time

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


class LoginForm(FlaskForm):
    name = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    if current_user.is_authenticated:
        user = User.query.all()[0]
        return render_template("index.html", user=user)
    else:
        if app.debug:
            login_user(User.query.filter(User.name == "admin").first())
        return redirect(url_for("login"))


@app.route('/file-upload', methods=['POST'])
@login_required
def file_upload():
    if 'file' not in request.files:
        return "Файлы не загружены", 403
    file = request.files['file']
    extension = get_extension_if_valid(file.filename)
    file_hash = hashlib.sha1((file.filename + str(random())).encode())
    if file and extension:
        if file.filename == '':
            return 'Пустое имя файла', 403
        filename = file_hash.hexdigest() + "." + extension
        path = join(app.static_folder, "files", "uploaded", filename)

        user = User.query.get(current_user.id)
        file_model = File(user.id, filename)
        user.files.append(file_model)
        db.session.commit()

        file.save(path)
        process_file.delay(path, filename)
        return jsonify(filename=filename, success=True)
    return "Расширение не поддерживается", 403


@app.route('/status', methods=['GET'])
def status():
    if current_user.is_authenticated:
        files = []
        for file in current_user.files:
            status_of_file = get_status_of_files()[file.filename]
            files.append({"status": status_of_file, "filename": file.filename})
        return render_template("status.html", files=files)
    else:
        return redirect(url_for("login"))


@app.route('/login', methods=['GET'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        return render_template("login.html", form=form)
    else:
        return redirect(url_for("index"))


@app.route('/login/process', methods=['GET', 'POST'])
def login_process():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.name == form.name.data).first()
        if user is None:
            flash('User not found.')
            return redirect(url_for('login'))
        if user.password != form.password.data:
            flash('Password is wrong.')
            return redirect(url_for('login'))
        login_user(user)
        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)
        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

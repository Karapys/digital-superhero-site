from app import app, celery, db, redis_client, process_file, get_status_of_files, redis_client
from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from app.utils import is_safe_url, get_extension_if_valid
from app.models import *
from os.path import join
from random import random
from functools import wraps
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


def create_admin():
    user = User(name="admin", password="admin")
    db.session.add(user)
    db.session.commit()
    return user


def redirect_without_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_function


@app.route('/')
def index():
    user = User.query.all()
    if len(user) == 0:
        user = create_admin()
    else:
        user = user[0]
    if current_user.is_authenticated:
        return render_template("index.html", user=user)
    else:
        if app.debug:
            login_user(user)
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
        path = join(app.static_folder, "files", "uploaded")

        user = User.query.get(current_user.id)
        file_model = File(user.id, filename)
        user.files.append(file_model)
        db.session.commit()

        file.save(join(path, filename))
        process_file.delay(path, filename)
        return jsonify(filename=filename, success=True)
    return "Расширение не поддерживается", 403


@app.route('/tasks', methods=['GET'])
@redirect_without_login
def status():
    files = []
    for file in current_user.files[::-1]:
        status_of_file = get_status_of_files()[file.filename]
        files.append({"status": status_of_file, "filename": file.filename, "id": file.id})
    return render_template("tasks.html", files=files)


@app.route('/task/<int:task_id>', methods=['GET'])
@redirect_without_login
def single_task(task_id):
    return redirect("/task/"+str(task_id)+"/photo-1")


@app.route('/task/<int:task_id>/photo-<int:photo_id>', methods=['GET'])
@redirect_without_login
def photo(task_id, photo_id):
    task = File.query.get(task_id)
    folder_name, files = pickle.loads(redis_client.get(task.filename))
    print(folder_name, files)
    print(files[photo_id-1])
    return render_template("single_task.html",
                           photo_id=str(photo_id),
                           folder_name=str(folder_name),
                           files=files)


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

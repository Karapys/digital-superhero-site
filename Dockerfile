# pull official base image
FROM python:3.8.1-slim-buster

# set project dir
ENV PROJECT_DIR /var/www/site
WORKDIR ${PROJECT_DIR}

# set environment variables
ENV DB_URI postgresql:///db
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:${PROJECT_DIR}/app:${PROJECT_DIR}"

# install dependencies
RUN pip install --upgrade pip

COPY ./requirements.txt /var/www/site/requirements.txt
RUN pip install -r requirements.txt

COPY app ${PROJECT_DIR}/app
WORKDIR ${PROJECT_DIR}/app
RUN rm -f db.sqlite3
RUN python init_default_db.py

EXPOSE 8080
CMD gunicorn -w 1 --bind 0.0.0.0:8080 --log-level debug wsgi:app


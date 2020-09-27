# pull official base image
FROM python:3.8.3

# set project dir
ENV PROJECT_DIR /var/www/site
WORKDIR ${PROJECT_DIR}

# set environment variables
ENV DB_URI postgresql:///db
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:${PROJECT_DIR}/app:${PROJECT_DIR}"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# install dependencies
RUN pip install --upgrade pip
# To make psycopg2 work
RUN apt-get update
RUN apt-get install 'ffmpeg' 'libsm6' 'libxext6' -y

COPY ./requirements.txt /var/www/site/requirements.txt
RUN pip install -r requirements.txt
RUN pip install opencv-python==4.2.0.34

COPY ./start.sh ${PROJECT_DIR}
COPY migrations ${PROJECT_DIR}/migrations
COPY app ${PROJECT_DIR}/app

RUN mkdir -p app/eo_learn/patch
RUN mkdir -p app/static/files/uploaded

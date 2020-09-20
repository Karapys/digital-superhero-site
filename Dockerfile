# pull official base image
FROM python:3.8.3-alpine

# set project dir
ENV PROJECT_DIR /var/www/site
WORKDIR ${PROJECT_DIR}

# set environment variables
ENV DB_URI postgresql:///db
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:${PROJECT_DIR}/app:${PROJECT_DIR}"

# install dependencies
RUN pip install --upgrade pip
# To make psycopg2 work
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt /var/www/site/requirements.txt
RUN pip install -r requirements.txt

COPY app ${PROJECT_DIR}/app
COPY ./start.sh ${PROJECT_DIR}
COPY migrations ${PROJECT_DIR}/migrations

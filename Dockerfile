# pull officail base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /usr/src/app

# set enviroment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN apt-get update
# RUN apt-get install -f vim
#RUN apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev linux-headers

COPY . /usr/src/app/

# install dependecies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
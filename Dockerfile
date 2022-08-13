
FROM python:3.7-buster

ENV TZ=Europe/Madrid

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
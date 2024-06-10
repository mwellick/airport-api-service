FROM python:3.12-slim
LABEL maintainer="mr.anderson528491@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

COPY airport_service_db_data.json airport_service_db_data.json

RUN mkdir -p /files/media

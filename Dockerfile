FROM python:3-alpine

LABEL maintainer="alexhall93@me.com"

EXPOSE 8081
RUN mkdir -p /var/app
WORKDIR /hub

RUN set -e; \
	apk add --no-cache --virtual .build-deps uwsgi-python3;

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN apk del .build-deps;

COPY ./uwsgi.ini uwsgi.ini

RUN mkdir spoolfiles

ENTRYPOINT ["uwsgi", "--ini=uwsgi.ini"]



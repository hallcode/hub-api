FROM python:3-alpine

LABEL maintainer="alexhall93@me.com"

EXPOSE 8081
RUN mkdir -p /usr/src
WORKDIR /usr/src

COPY ./requirements.txt requirements.txt
RUN set -e; \
	apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev linux-headers \
	                              libc-dev libffi-dev libressl-dev; \
	apk add postgresql-dev; \
	pip install --no-cache-dir -r requirements.txt; \
	apk del .build-deps; \
	mkdir spoolfiles; chmod 664 spoolfiles

COPY ./migrations ./migrations
COPY ./uwsgi.ini uwsgi.ini
COPY ./spawn.sh spawn.sh
ENV FLASK_APP=hub

ENTRYPOINT ["./spawn.sh"]



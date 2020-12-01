FROM tiangolo/uwsgi-nginx-flask:python3.8

MAINTAINER Alex Hall "alexhall93@me.com"

ENV NGINX_MAX_UPLOAD 64m

WORKDIR /var/www

ENV UWSGI_INI uwsgi.ini

COPY ./requirements.txt requirements.txt
COPY ./uwsgi.ini uwsgi.ini
COPY ./migrations /migrations

RUN pip install -r requirements.txt
RUN mkdir spoolfiles



FROM tiangolo/uwsgi-nginx-flask:python3.8
ENV NGINX_MAX_UPLOAD 64m
RUN apk --update add bash nano

WORKDIR /var/www

ENV UWSGI_INI uwsgi.ini

COPY ./requirements.txt requirements.txt
COPY ./uwsgi.ini uwsgi.ini

RUN pip install -r requirements.txt



#! /usr/bin/env sh
set -e

flask db upgrade

/usr/local/bin/uwsgi --ini=uwsgi.ini
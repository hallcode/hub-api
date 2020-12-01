#!/usr/bin/env bash

app="hub-api"

docker build -t ${app} .
docker run -d -p 8080:80 --name=${app} -v "$PWD"/hub:/var/www/hub ${app}
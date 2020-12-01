#!/usr/bin/env bash

app="hub-api"

docker build -t ${app} .
docker run -d -p 80100:80 --name=${app} -v $PWD:/hub ${app}
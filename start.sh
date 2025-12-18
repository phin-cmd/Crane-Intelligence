#!/bin/sh
cd /root/crane
docker-compose build
docker-compose up -d
sleep 3
docker-compose ps


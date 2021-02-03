#!/bin/bash

echo "Start deploy..."

docker-compose up -d --build
docker-compose exec web python manage.py collectstatic --no-input --clear
docker-compose exec web python manage.py test --no-input
docker-compose exec -u root web /usr/bin/crontab crontab.txt
docker-compose exec -d -u root web /usr/sbin/crond -f -l 8

echo "-----> Deploy is finished successfully"

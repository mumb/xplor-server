#!/usr/bin/env bash
sleep 15
python manage.py  collectstatic --no-input
python manage.py migrate
python manage.py loaddata seed.json
python manage.py runserver 0.0.0.0:8000

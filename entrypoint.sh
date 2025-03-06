#!/bin/sh
python manage.py migrate

python manage.py loaddata

exec uvicorn main:app --host 0.0.0.0 --port 9000
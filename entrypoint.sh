#!/bin/sh
python manage.py migrate
python manage.py loaddata estados.json cidades.json
python manage.py createsuperuser --noinput

# Inicia o servidor Django
exec "$@"

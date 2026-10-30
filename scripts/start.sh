#!/bin/sh
# Prepara os volumes e sobe o servidor
set -e

MEDIA=/var/www/html/Morea/media

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# O volume de mídia nasce vazio: recoloca as imagens padrão e a pasta dos gráficos
mkdir -p "$MEDIA/defaults" "$MEDIA/graphs"
cp -n media/defaults/* "$MEDIA/defaults/"

exec gunicorn morea_ds.wsgi:application -b 0.0.0.0:8000

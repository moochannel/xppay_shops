#!/usr/bin/env bash

# if command starts with an option, prepend gunicorn
if [ "${1:0:1}" = '-' ]; then
	set -- gunicorn "$@"
fi

_update_data() {
	echo "Initializing data..."
    python manage.py migrate
    python manage.py collectstatic --noinput
    python manage.py loaddata areas.yaml
    python manage.py loaddata contact_types.yaml
    python manage.py loaddata demo-shops.yaml
	echo "done"
}

_update_data

echo "Booting gunicorn"
exec "$@"

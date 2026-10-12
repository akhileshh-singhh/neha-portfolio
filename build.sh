#!/usr/bin/env bash
# Render / Railway build step
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_site      # only loads starter content if the site is empty
python manage.py ensure_admin   # creates the login from DJANGO_SUPERUSER_* env vars (skipped if unset)

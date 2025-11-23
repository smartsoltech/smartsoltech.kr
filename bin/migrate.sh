#!/usr/bin/env bash
# Run migrations
docker exec ${django_app} python3 smartsoltech/manage.py migrate
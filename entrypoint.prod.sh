#!/bin/sh

gunicorn wsgi:app --bind 0.0.0.0:8000
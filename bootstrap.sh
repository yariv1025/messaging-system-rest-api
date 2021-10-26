#!/bin/sh

export FLASK_APP=./src/app.py
#source $(pipenv --venv)/bin/activate
export FLASK_ENV=development

flask run --host=127.0.0.1 --port=5000
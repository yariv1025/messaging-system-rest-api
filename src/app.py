from flask import Flask, Blueprint
from bson import json_util
from bson.py3compat import PY3
import collections.abc as abc
from abc import ABC, abstractmethod
from src import routes
from src.database.db import DataBase as db


def create_app():
    # app initialization
    app = Flask(__name__)

    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
    elif app.config["ENV"] == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    # db initialization
    collection = db.get_instance(app)

    for blueprint in vars(routes).values():
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint)

    return app, collection


if __name__ == '__main__':
    app, collection = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)

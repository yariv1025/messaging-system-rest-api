import config

from flask import Flask, Blueprint
from api.database.db import DataBase as db


def create_app():
    # app initialization
    app = Flask(__name__)

    # app configuration
    app.config.from_object(config.exportConfig)

    # database initialization
    collection = db.get_instance(app)

    # blueprints registering
    from api.routes import v1 as routes
    blueprints_candidate = vars(routes).values()
    blueprints_list = list(filter(lambda blueprint: isinstance(blueprint, Blueprint), blueprints_candidate))
    [app.register_blueprint(blueprint) for blueprint in blueprints_list]

    return app

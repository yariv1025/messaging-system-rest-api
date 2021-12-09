import config

from flask import Flask, Blueprint

from api.database.mongo import DataBase as db
from api.errors import register_error_handlers


def create_app():
    # app initialization
    app = Flask(__name__)

    # app configuration
    app.config.from_object(config.exportConfig)

    # register error handlers
    register_error_handlers(app)

    try:
        # database initialization
        collection = db.get_instance(app)

    except Exception as e:
        return {"Error: ", str(e)}

    # blueprints registering
    from api.routes import v1 as routes
    blueprints_candidate = vars(routes).values()
    blueprints_list = list(filter(lambda blueprint: isinstance(blueprint, Blueprint), blueprints_candidate))
    [app.register_blueprint(blueprint) for blueprint in blueprints_list]

    return app

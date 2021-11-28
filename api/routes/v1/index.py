from flask import Blueprint
from api.seed.seeder import seed

index_blueprint = Blueprint("index", __name__)


@index_blueprint.route('/')
def home_page():
    """
    Home page
    :return: message response
    """
    return "Messaging System - REST API!"


@index_blueprint.route('/seed', methods=['POST'])
def seed_db():
    """
    Performs seeding to mongo db
    :return: message response
    """
    return seed()

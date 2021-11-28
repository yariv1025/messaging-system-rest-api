from flask import Blueprint

from api.seed.seeder import seed

seed_blueprint = Blueprint("seed", __name__)


@seed_blueprint.route('/seed', methods=['POST'])
def seed_db():
    """
    Performs seeding to mongo db
    :return: message response
    """
    return seed()

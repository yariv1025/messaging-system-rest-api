from flask import Blueprint

from api.controllers.token import refresh

token_blueprint = Blueprint("token", __name__)


@token_blueprint.route('/oauth/refresh', methods=['POST'])
def refresh_token():
    """
    Postman exam: WEB_ROUTE/oauth/token
    :return: new access token
    """
    return refresh()

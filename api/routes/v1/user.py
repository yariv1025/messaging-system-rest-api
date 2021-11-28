from api.controllers.token import refresh
from api.database.db import DataBase
from api.controllers.user import *
from api.validations import *

user_blueprint = Blueprint("user", __name__)
collection = DataBase.get_instance()


@user_blueprint.route('/user', methods=['POST'])
@validate_request("user", "register")
def set_user(user_data):
    """
    signup
    Postman exam: WEB_ROUTE/user
    :return:
    """
    return signup(collection, user_data)


@user_blueprint.route('/oauth/login', methods=['POST'])
@validate_request("user", "login")
def login_user(user_data):
    """
    Login
    Postman exam: WEB_ROUTE/auth/login?email=VALID_EMAIL&password=PASSWORD
    :return: user details
    """
    return login(collection, user_data)


@user_blueprint.route('/oauth/logout', methods=['POST'])
@authorize_required
def logout_user(data):
    """
    Postman exam: WEB_ROUTE/oauth/logout
    :return: response
    """
    # Note: Need to implement Token Revoking/Blocklisting
    # Info: https://flask-jwt-extended.readthedocs.io/en/latest/blocklist_and_token_revoking/
    # Info: https://darksun-flask-jwt-extended.readthedocs.io/en/latest/blacklist_and_token_revoking/
    return logout()


@user_blueprint.route('/oauth/token', methods=['POST'])
def refresh_token():
    """
    Postman exam: WEB_ROUTE/oauth/token
    :return: new access token
    """
    return refresh()
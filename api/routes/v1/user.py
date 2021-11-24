from api.controllers.token import refresh
from api.seed.seeder import seed
from api.database.db import DataBase
from api.controllers.user import *
from api.validations import *

user_blueprint = Blueprint("user", __name__)
collection = DataBase.get_instance()


@user_blueprint.route('/')
def home_page():
    """
    Home page
    :return: message response
    """
    return "Messaging System - REST API!"


@user_blueprint.route('/seed', methods=['POST'])
def seed_db():
    """
    Performs seeding to mongo db
    :return: message response
    """
    return seed()


@user_blueprint.route('/messages', methods=['GET'])
@authorize_required
def get_messages(user_data):
    """
    Get all read messages / unread messages
    Postman exam: WEB_ROUTE/messages?only_unread=True
    :param user_data: user details
    :return: all messages for a specific user
    """
    return read_all_messages(collection, user_data)


@user_blueprint.route('/messages/<string:messageId>', methods=['GET'])
@authorize_required
def get_single_message(user_data, **kwargs):
    """
    Get message by id
    Postman exam: WEB_ROUTE/messages/MESSAGE_ID_FROM_MONGO_DB
    :param user_data: user details
    :return: Details of one message
    """
    return read_message(collection, kwargs["messageId"], user_data)


@user_blueprint.route('/messages/<string:messageId>', methods=['DELETE'])
@authorize_required
def delete(user_data, **kwargs):
    """
    Delete specific message by id
    Postman exam: WEB_ROUTE/messages/MESSAGE_ID_FROM_MONGO_DB
    :param user_data: data details
    :return: response / feedback
    """
    return delete_message(collection, kwargs["messageId"], user_data)


@user_blueprint.route('/messages', methods=['POST'])
@authorize_required
@validate_request("message", "create")
def set_message(user_data, message):
    """
    Post message
    Postman exam: WEB_ROUTE/messages
    :param user_details: user details
    :param message: user message
    :return: message id
    """
    return write_message(collection, user_data, message)


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


# TODO: fix logout function
# TODO: Refactoring message calls and Object creation
# TODO: Refactoring user model calls and methods
# TODO: Create tests

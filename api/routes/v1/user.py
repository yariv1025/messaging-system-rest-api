from werkzeug.exceptions import BadRequestKeyError
from flask import Blueprint, request, json

from api.controllers.token import refresh_token
from api.utilities import authorize_required, json_resp
from api.seed.seeder import seed
from api.database.db import DataBase
from api.controllers import user as user_controller

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
def get_messages(data):
    """
    Get all read messages / unread messages
    Postman exam: WEB_ROUTE/messages?only_unread=True
    :param data: user details
    :return: all messages for a specific user
    """
    try:
        only_unread = request.args.get('only_unread')

    except BadRequestKeyError as e:
        return json_resp({"message": "Missing parameter", "exception": str(e)}, 400)

    user_id = json.loads(data["user_id"])["$oid"]
    return user_controller.read_all(collection, user_id, only_unread)


@user_blueprint.route('/messages/<string:messageId>', methods=['GET'])
@authorize_required
def get_single_message(data, **kwargs):
    """
    Get message by id
    Postman exam: WEB_ROUTE/messages/MESSAGE_ID_FROM_MONGO_DB
    :param data: user details
    :return: Details of one message
    """
    user_id = json.loads(data["user_id"])["$oid"]
    return user_controller.read(collection, kwargs["messageId"], user_id)


@user_blueprint.route('/messages/<string:messageId>', methods=['DELETE'])
@authorize_required
def delete_single_message(data, **kwargs):
    """
    Delete specific message by id
    Postman exam: WEB_ROUTE/messages/MESSAGE_ID_FROM_MONGO_DB
    :param data: data details
    :return: response / feedback
    """
    user_id = json.loads(data["user_id"])["$oid"]
    return user_controller.delete(collection, kwargs["messageId"], user_id)


@user_blueprint.route('/messages', methods=['POST'])
@authorize_required
def post_message(data):
    """
    Post message
    Postman exam: WEB_ROUTE/messages
    :param data: user details
    :return: message id
    """
    user_id = json.loads(data["user_id"])["$oid"]
    return user_controller.write(collection, user_id)


@user_blueprint.route('/user', methods=['POST'])
def signup():
    """
    signup
    Postman exam: WEB_ROUTE/user
    :return:
    """
    return user_controller.signup(collection)


@user_blueprint.route('/oauth/login', methods=['POST'])
def login():
    """
    Login
    Postman exam: WEB_ROUTE/auth/login?email=VALID_EMAIL&password=PASSWORD
    :return: user details
    """
    return user_controller.login(collection)


@user_blueprint.route('/oauth/logout', methods=['POST'])
@authorize_required
def logout(data, **kwargs):
    """
    Postman exam: WEB_ROUTE/oauth/logout
    :return:
    """
    # Note: Need to implement Token Revoking/Blacklisting
    # Info: https://flask-jwt-extended.readthedocs.io/en/latest/blocklist_and_token_revoking/
    # Info: https://darksun-flask-jwt-extended.readthedocs.io/en/latest/blacklist_and_token_revoking/
    return user_controller.logout()


@user_blueprint.route('/oauth/token', methods=['POST'])
def token():
    """
    Postman exam: WEB_ROUTE/oauth/token
    :return: new access token
    """
    return refresh_token()


# TODO: fix logout function
# TODO: Refactoring message calls and Object creation
# TODO: Refactoring user model calls and methods
# TODO: Create tests

import config

from api.auth import authorize_user
from flask import Blueprint, request
from jose import jwt
from api import tools
from api.seed.seeder import seed
from api.models.users import User
from api.database.db import DataBase as db, DataBase

from api.controllers import users

user_blueprint = Blueprint("user", __name__)
conf = config.exportConfig.SECRET_KEY
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

    seed()
    return "SEED"


@user_blueprint.route('/messages', methods=['GET'])
@authorize_user
def get_messages(user, user_id):
    """
    Get all read messages / unread messages
    Postman exam: WEB_ROUTE/messages?only_unread=True
    :param user: user instance
    :param user_id: user id
    :return: all messages for a specific user
    """
    only_unread = request.args.get('only_unread')
    return users.read_all(collection, user, user_id, only_unread)


@user_blueprint.route('/messages/<string:messageId>', methods=['GET'])
@authorize_user
def get_message(user, user_id, messageId):
    """
    Get message by id
    Postman exam: WEB_ROUTE/messages/MESSAGE_ID_FROM_MONGO_DB
    :param user: user instance
    :param user_id: user id
    :param messageId: message identification number
    :return: Details of one message
    """
    return users.read(collection, user, messageId["messageId"], user_id)


@user_blueprint.route('/messages/<string:messageId>', methods=['DELETE'])
@authorize_user
def delete_message(user, user_id, messageId):
    """
    Delete specific message by id
    Postman exam: WEB_ROUTE/user/messages/delete/MESSAGE_ID_FROM_MONGO_DB
    :param user: user instance
    :param user_id: user id
    :param messageId: message id
    :return: response / feedback
    """
    return users.delete(collection, user, messageId["messageId"], user_id)
    # return users.delete(collection, user, messageId["messageId"], user_id)


@user_blueprint.route('/messages', methods=['POST'])
@authorize_user
def post_message(user, user_id):
    """
    Post message
    Postman exam: WEB_ROUTE/messages/write?sender=SENDER_FULL_NAME&receiver=RECEIVER_FULL_NAME&subject=SUBJECT&message=MESSAGE
    :param user: user instance
    :param user_id: user id
    :return: message id
    """
    return users.write(collection, user, user_id)


@user_blueprint.route('/user', methods=['POST'])
def signup():
    """
    signup
    Postman exam: WEB_ROUTE/user/signup?first_name=FIRST_NAME&last_name=LAST_NAME&email=VALID_EMAIL&password=PASSWORD
    :return:
    """

    # Get param & create the User object
    user = User(request.args['first_name'],
                request.args['last_name'],
                request.args['email'].lower(),
                request.args['password'])
    return user.create_user(collection)


@user_blueprint.route('/auth/login', methods=['POST'])
def login():
    """
    Login
    Postman exam: WEB_ROUTE/user/login?email=VALID_EMAIL&password=PASSWORD
    :return: user details
    """
    # return User.login(collection)
    return users.login(collection)


@user_blueprint.route('/auth/logout', methods=['GET'])
@authorize_user
def logout(user, user_id):
    """
    Postman exam: WEB_ROUTE/sign-out
    :return:
    """

    try:
        print("SECRET_KEY: ", conf.SECRET_KEY)

        access_token = request.headers['Authorization'].split()[1]
        print("access_token: ", access_token)

        token_data = jwt.decode(access_token, conf.SECRET_KEY)
        print("token_data: ", token_data)

        resp = conf.collection.tokens.update({"id": token_data["user_id"]}, {'$set': {"refresh_token": ""}},
                                             upsert=True)

        print("resp: ", resp)
        exit(0)
        # Note: At some point I need to implement Token Revoking/Blacklisting
        # General info here: https://flask-jwt-extended.readthedocs.io/en/latest/blacklist_and_token_revoking.html

        resp = tools.JsonResp({"message": "User logged out"}, 200)
        print("resp: ", resp)
        return resp

    except Exception as e:
        return {"error": str(e)}, 500

# TODO: fix authentication: activate refresh token
# TODO: fix logout function

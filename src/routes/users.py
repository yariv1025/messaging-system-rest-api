import config
from flask import Blueprint, request
from jose import jwt
from src import tools
from src.seed.seeder import seed
from src.models.users import User
from src.database.db import DataBase as db

user_blueprint = Blueprint("user", __name__)
conf = config.Config()


def authorize_user(func):
    """
    Extension of code on an existing function.
    The authorize_user decorator performs authentication and then returns to the original function
    :param func: Another function
    :return: original func(user_id) with user id as arg
    """

    # Authorization
    def wrapper(**kwargs):
        collection = db.get_instance()
        access_token = request.headers['Authorization'].split()[1]
        token = collection.tokens.find_one({"access_token": access_token})

        if token:
            user_schema = collection.users.find_one(token["user_id"])
            user = User.get_user_instance(user_schema)
            if kwargs:
                return func(user, token["user_id"], kwargs)
            return func(user, token["user_id"])

        else:
            return tools.JsonResp("Unauthorized access", 401)

    # Change wrapper name to prevent AssertionError when
    # I tried to wrap more than one function with the decorator
    wrapper.__name__ = func.__name__
    return wrapper


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
    collection = db.get_instance()
    seed(collection)
    return "SEED"


@user_blueprint.route('/user/messages/all-messages', methods=['GET'])
@authorize_user
def get_messages(user, user_id):
    """
    Get all user messages
    Postman exam: WEB_ROUTE/user/messages/all-messages
    :param user: user instance
    :param user_id: user id
    :return: all messages for a specific user
    """
    collection = db.get_instance()
    return user.read_messages(collection, user_id, True)


@user_blueprint.route('/user/messages/unread', methods=['GET'])
@authorize_user
def get_unread_messages(user, user_id):
    """
     Get all unread user messages
     Postman exam: WEB_ROUTE/user/messages/unread
    :param user: user instance
    :param user_id: user id
    :return: all unread messages for a specific user
    """
    collection = db.get_instance()
    return user.read_messages(collection, user_id, False)


@user_blueprint.route('/user/messages/<string:messageId>', methods=['GET'])
@authorize_user
def read_message(user, user_id, messageId):
    """
    Get specific user message by id
    Postman exam: WEB_ROUTE/user/messages/MESSAGE_ID_FROM_MONGO_DB
    :param user: user instance
    :param user_id: user id
    :param messageId: message identification number
    :return: Details of one message
    """
    collection = db.get_instance()
    return user.read_message(collection, messageId["messageId"], user_id)


@user_blueprint.route('/user/messages/delete/<string:messageId>', methods=['DELETE'])
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
    collection = db.get_instance()
    return user.delete_message(collection, messageId["messageId"], user_id)


@user_blueprint.route('/user/messages/write', methods=['POST'])
@authorize_user
def write_messages(user, user_id):
    """
    Writing a message
    Postman exam: WEB_ROUTE/user/messages/write?sender=SENDER_FULL_NAME&receiver=RECEIVER_FULL_NAME&subject=SUBJECT&message=MESSAGE
    :param user: user instance
    :param user_id: user id
    :return: message id
    """
    collection = db.get_instance()
    return user.send_message(collection, user_id)


@user_blueprint.route('/user/signup', methods=['POST'])
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
    collection = db.get_instance()
    return user.create_user(collection)


@user_blueprint.route('/user/login', methods=['POST'])
def login():
    """
    Login
    Postman exam: WEB_ROUTE/user/login?email=VALID_EMAIL&password=PASSWORD
    :return: user details
    """
    collection = db.get_instance()
    return User.login(collection)


@user_blueprint.route('/user/logout', methods=['GET'])
@authorize_user
def logout(user, user_id):
    """
    Postman exam: WEB_ROUTE/sign-out
    :return:
    """

    try:
        collection = db.get_instance()
        print("SECRET_KEY: ", conf.SECRET_KEY)

        access_token = request.headers['Authorization'].split()[1]
        print("access_token: ", access_token)

        token_data = jwt.decode(access_token, conf.SECRET_KEY)
        print("token_data: ", token_data)

        resp = collection.tokens.update({"id": token_data["user_id"]}, {'$set': {"refresh_token": ""}}, upsert=True)

        print("resp: ", resp)
        exit(0)
        # Note: At some point I need to implement Token Revoking/Blacklisting
        # General info here: https://flask-jwt-extended.readthedocs.io/en/latest/blacklist_and_token_revoking.html

        resp = tools.JsonResp({"message": "User logged out"}, 200)
        print("resp: ", resp)
        return resp

    except Exception as e:
        return {"error": str(e)}, 500

import ast
import os

from bson import json_util
from flask import Flask
from flask_pymongo import PyMongo
from src import auth
from src.seed.seeder import seed
from src.users.models import *

# app initialization
app = Flask(__name__)

# mongoDB configuration & initialization
app.config['MONGO_DBNAME'] = 'messages'
password = "Mongo1805"
username = "yariv1052"
app.config[
    'MONGO_URI'] = f'mongodb+srv://{username}:{password}@cluster0.jryya.mongodb.net/messaging_system?retryWrites=true&w=majority'

# Create mongoDB client
mongo_client = PyMongo(app)
collection = mongo_client.db


def authorize_user(func):
    """
    Extension of code on an existing function.
    The authorize_user decorator performs authentication and then returns to the original function
    :param func: Another function
    :return: original func(user_id) with user id as arg
    """

    # Authorization
    def wrapper(**kwargs):

        access_token = request.headers['Authorization'].split()[1]
        token = collection.tokens.find_one({"access_token": access_token})

        if token:
            return func(token["user_id"], kwargs)
        else:
            return tools.JsonResp("Unauthorized access", 401)

    # Change wrapper name to prevent AssertionError when
    # I tried to wrap more than one function with the decorator
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
def home_page():
    """
    Home page
    :return: message response
    """
    return "Messaging System - REST API!"


@app.route('/seed', methods=['POST'])
def seed_db():
    """
    Performs seeding to mongo db
    :return: message response
    """
    seed(collection)
    return "SEED"


@app.route('/get-all-messages', methods=['GET'])
@authorize_user
def get_all_messages(user_id, args):
    """
    Get from "read_all_messages()" method all user messages
    :param user_id: user id
    :param args: args
    :return: all messages for a specific user
    """
    return User.read_all_messages(collection, user_id)


@app.route('/get-unread-messages', methods=['GET'])
@authorize_user
def get_unread_messages(user_id, args):
    """
     Get from "read_unread_messages()" method all unread user messages
    :param user_id: user id
    :param args: args
    :return: all unread messages for a specific user
    """
    return User.read_unread_messages(collection, user_id)


@app.route('/read-message/<string:messageId>', methods=['GET'])
@authorize_user
def read_message(user_id, messageId):
    """
    Calling to read_message() method to query one and specific message
    :param user_id: user id
    :param messageId: message identification number
    :return: Details of one message
    """
    return User.read_message(collection, messageId["messageId"], user_id)


@app.route('/delete-message/<string:messageId>', methods=['DELETE'])
@authorize_user
def delete_message(user_id, messageId):
    """
    Calling to delete_message() method to delete one and specific message by id
    :param user_id: user id
    :param messageId: message id
    :return: response / feedback
    """
    return User.delete_message(collection, messageId["messageId"], user_id)


# Write message
@app.route('/write-messages', methods=['POST'])
@authorize_user
def write_messages(user_id, args):
    """
    Calling to send_message() method to writing a message
    :param user_id:
    :param args:
    :return:
    """
    return User.send_message(collection, user_id)


# User creation
@app.route('/user', methods=['POST'])
def create_user():
    """
    User creation
    :return:
    """

    # Get param & create the User object
    user = User(request.args['first_name'],
                request.args['last_name'],
                request.args['email'].lower(),
                request.args['password'])

    return user.create_user(collection)


@app.route('/login', methods=['POST'])
def login():
    """
    User login
    :return: user details
    """

    try:
        # Get param & create the User object
        login_details = {"email": request.args['email'].lower(),
                         "password": request.args['password']}

        # Looking for user
        user_response = collection.users.find_one({"email": login_details['email']})

        if pbkdf2_sha256.verify(login_details["password"], user_response["password"]) and user_response:
            """
            Check:
            - that the password in the database is not the old hash
            - that the password in the database is a correct hash of the password
            - that the user is exist
            """

            user_id = json.dumps(user_response['_id'], default=json_util.default)

            access_token = auth.encodeAccessToken(user_id, user_response["email"])
            refresh_token = auth.encodeRefreshToken(user_id, user_response["email"])

            # TODO: Fix & replace with update method from User class
            collection.tokens.update_many({"user_id": ObjectId(user_response['_id'])},
                                          {"$set": {"access_token": access_token,
                                                    "refresh_token": refresh_token,
                                                    "last_login": tools.nowDatetimeUTC()
                                                    }}, upsert=True)

            resp = tools.JsonResp({
                "id": user_response["_id"],
                "email": user_response["email"],
                "first_name": user_response["first_name"],
                "last_name": user_response["last_name"],
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200)

            return resp

        else:
            return tools.JsonResp({"message": "Invalid user credentials"}, 403)

    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/sign-out', methods=['GET'])
def logout():
    # try:
    # TODO: Temporary SECRET_KEY!! -> config.cfg file needed fixing
    # SECRET_KEY = 'aQ70AYYoi4'
    # token_data = jwt.decode(request.headers.get("AccessToken"), SECRET_KEY)
    # print("token_data: ", token_data)
    # collection.users.update({"id": token_data["user_id"]}, {'$unset': {"refresh_token": ""}})
    #
    # Implement logout & token revoking/blacklisting needed
    # Info : https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking/

    # except Exception as e:
    #     return {"error": str(e)}, 500
    pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

# TODO: Refactoring:
# 1: Handle error returns
# 2: Grab variables from "environment variables" -> (config.cfg file)
# 3: Fix methods -> from static to instance
# 4: Change method name convention to camelCase
# 5: Move authorize_user() decorator to __init__.py -> auth dir
# 6: Fixing "update_is_read_flag()" method -> User method
# 7: Fixing "login()" method -> User method
# 7: Fixing "logout()" method

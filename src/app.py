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

# Determining environment
isProduction = False if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == "development" else True

# usr = os.environ['MONGO_DB_USER']
# pwd = os.environ['MONGO_DB_PASS']

password = "YOUR_PASSWORD"
username = "YOUR_USERNAME"

mongo_uri = ""
if isProduction:
    mongo_uri = f'mongodb+srv://{username}:{password}@cluster0.jryya.mongodb.net/messaging_system?retryWrites=true&w=majority'
else:
    mongo_uri = f'mongodb+srv://{username}:{password}@cluster0.jryya.mongodb.net/messaging_system?retryWrites=true&w=majority'
print("mongo_uri: ", mongo_uri)
app.config['MONGO_URI'] = mongo_uri

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


#  Home page
@app.route('/')
def home_page():
    return "Messaging System - RESTful API!"


#  Home page
@app.route('/seed', methods=['POST'])
def seed_db():
    seed(collection)
    return "SEED"


# Get all unread messages for specific user
@app.route('/get-all-messages', methods=['GET'])
@authorize_user
def get_all_messages(user_id, args):
    """
    Reading all user messages
    :param user_id: user id
    :param args: args
    :return:  all messages for a specific user
    """

    try:
        return User.read_all_messages(collection, user_id)

    except Exception as e:
        return {"error": str(e)}, 500


# Get all unread messages for specific user
@app.route('/get-unread-messages', methods=['GET'])
@authorize_user
def get_unread_messages(user_id, args):
    """
    Reading all user unread messages
    :param user_id: user id
    :param args: args
    :return: all unread messages for a specific user
    """

    try:
        return User.read_unread_messages(collection, user_id)

    except Exception as e:
        return {"error": str(e)}, 500


# Get only one message by id
@app.route('/read-message/<string:messageId>', methods=['GET'])
@authorize_user
def read_message(user_id, messageId):
    """
    Query message where the `id` field equal messageId
    :param user_id: user id
    :param messageId: message identification number
    :return: Details of one message
    """

    try:
        return User.read_message(collection, messageId["messageId"], user_id)

    except Exception as e:
        return {"error": str(e)}, 500


# Delete message (as owner or as receiver)
@app.route('/delete-message/<string:messageId>', methods=['DELETE'])
@authorize_user
def delete_message(user_id, messageId):
    """
    Delete one message by id
    :param user_id: user id
    :param messageId: message id
    :return: response / feedback
    """

    try:
        response = User.delete_message(collection, messageId)
        return tools.JsonResp(response.deleted_count, 200)
        # return {
        #     "status_code": 200,
        #     "Amount of deleted message:": json.dumps(response.deleted_count, default=json_util.default)
        # }

    except Exception as e:
        return {"error": str(e)}, 500


# Write message
@app.route('/write-messages', methods=['POST'])
@authorize_user
def write_messages(user_id, args):
    try:
        return User.send_message(collection, user_id)

    except Exception as e:
        return {"error": str(e)}, 500


# User creation
@app.route('/user', methods=['POST'])
def create_user():
    # Get param & create the User object
    user = User(request.args['first_name'],
                request.args['last_name'],
                request.args['email'].lower(),
                request.args['password'])

    # Looking for user
    user_response = collection.users.find_one({"email": request.args['email'].lower()})

    if tools.validEmail(request.args['email']) and user_response is None:

        try:
            response = user.save(collection)
            return tools.JsonResp(response.inserted_id, 200)

        except Exception as e:
            return {"error": str(e)}, 500

    else:
        return {"message": "There's already an account with this email address",
                "error": "email_exists"
                }, 409


@app.route('/login', methods=['POST'])
def login():
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

# TODO: Check to handle error returns
# TODO: Grab user/pass from the environment variables (config.cfg file)
# TODO: Fix methods -> from static to instance
# TODO: Change method name convention to camelCase
# TODO: Move authorize_user() to __init__.py in auth dir

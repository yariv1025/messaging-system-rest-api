import ast
import os

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

password = ""
username = ""

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


# TODO: Move authorize_user() to __init__.py in auth dir
def authorize_user(func):
    """
    Extension of code on an existing function.
    The authorize_user decorator performs authentication and then returns to the original function
    :param func: Another function
    :return: original func(user_id) with user id as arg
    """

    # Authorization
    def wrap_auth_check(**kwargs):

        access_token = request.headers['Authorization'].split()[1]
        token = collection.tokens.find_one({"access_token": access_token})

        if token:
            print("token: ", token)
            print("token[user_id]: ", token["user_id"])
            return func(token["user_id"], kwargs)
        else:
            return tools.JsonResp("Unauthorized access", 401)

    return wrap_auth_check


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
def get_all_messages():
    """
    Read all user messages
    :return: all messages for a specific user as a JSON file
    """

    try:
        return User.read_all_messages(collection)

    except Exception as e:
        return {"error": str(e)}, 500


# Get all unread messages for specific user
@app.route('/get-all-messages/<is_read>', methods=['GET'])
def get_all_unread_messages(is_read):
    pass


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

    # TODO:
    # 1) Get user id -> X
    # 2) Query the user from db -> X
    # 2) Check authentication -> X
    # 3) get message by id -> X

    try:
        return User.read_message(collection, messageId["messageId"])

    except Exception as e:
        return {"error": str(e)}, 500


# Delete message (as owner or as receiver)
@app.route('/delete-message/<string:messageId>', methods=['DELETE'])
def delete_message(messageId):
    """
    Delete one message by id
    :param messageId: message id
    :return: response / feedback
    """

    try:
        return User.delete_message(collection, messageId)

    except Exception as e:
        return {"error": str(e)}, 500


# Write message
@app.route('/write-messages', methods=['POST'])
def write_messages():
    # 1) Get user id -> query the user from db
    # 2) Get receiver id
    # 3) Check authentication
    # 4) user.send_message(collection)
    try:
        return User.send_message(collection)

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


@app.route('/sign-in', methods=['POST'])
def login():
    try:
        # Get param & create the User object
        sign_in_details = {"email": request.args['email'].lower(),
                           "password": request.args['password']}

        # Looking for user
        user_response = collection.users.find_one({"email": request.args['email'].lower()})

        if pbkdf2_sha256.verify(sign_in_details["password"], user_response["password"]) and user_response:
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


# TODO: Delete?
def create_update_list(internal_update=None):
    fields_to_updates = {}

    for key, value in request.args.items():
        fields_to_updates["key"] = value

    return fields_to_updates


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

# TODO: Check to handle error returns
# TODO: Grab user/pass from the environment variables (config.cfg file)
# TODO: Fix methods -> from static to instance
# TODO: Change method name convention to camelCase

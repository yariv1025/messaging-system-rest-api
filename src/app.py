import ast
import os

from bson import ObjectId
from flask import Flask
from flask_pymongo import PyMongo

from src import auth
from src.seed.seeder import seed
from src.users.models import *
from src.messages.models import Message

# app initialization
app = Flask(__name__)

# mongoDB configuration & initialization
app.config['MONGO_DBNAME'] = 'messages'

# Determining environment
isProduction = False if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == "development" else True

# usr = os.environ['MONGO_DB_USER']
# pwd = os.environ['MONGO_DB_PASS']

password = "Mongo1805"
username = "yariv1052"

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


#  Home page
@app.route("/")
def home_page():
    return "Messaging System - RESTful API!"


#  Home page
@app.route("/seed", methods=['POST'])
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
        return {
            "status_code": 500,
            "message": str(e)
        }


# Get all unread messages for specific user
@app.route('/get-all-messages/<is_read>', methods=['GET'])
def get_all_unread_messages(is_read):
    pass


# Get only one message by id
@app.route('/read-message/<string:messageId>', methods=['GET'])
def read_message(messageId):
    """
    Query message where the `id` field equal messageId
    :param messageId: message identification number
    :return: Details of one message
    """

    # TODO:
    # 1) Get user id -> DONE
    # 2) Query the user from db -> X
    # 2) Check authentication -> X
    # 3) get message by id -> X
    try:
        return User.read_message(collection, messageId)

    except Exception as e:
        return {
            "status_code": 500,
            "message": str(e)
        }


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
        return {
            "status_code": 500,
            "message": str(e)
        }


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
        return {
            "status_code": 500,
            "message": str(e)
        }


# User creation
@app.route('/user', methods=['POST'])
def create_user():
    # Get param & create the User object
    user = User(request.args['first_name'],
                request.args['last_name'],
                request.args['email'].lower(),
                request.args['password'])

    # Make sure there isn"t already a user with this email address
    existing_email = collection.users.find_one({"email": request.args['email'].lower()})

    if tools.validEmail(request.args['email']) and existing_email is None:

        try:
            response = user.save(collection)
            return Response(json.dumps(response.inserted_id, default=json_util.default), mimetype="application/json")

        except Exception as e:
            return {"error": str(e)
                    }, 500

    else:
        return {
                   "message": "There's already an account with this email address",
                   "error": "email_exists"
               }, 409


@app.route('/user', methods=['POST'])
def login():
    # response_user = user.save(collection)
    # user_id = ast.literal_eval(json.dumps(response_user.inserted_id, default=json_util.default))["$oid"]
    #
    # # Log the user in (create and return tokens)
    # access_token = auth.encodeAccessToken(user_id, user.get_user()["email"])
    # refresh_token = auth.encodeRefreshToken(user_id, user.get_user()["email"])
    #
    # data_to_update = {"refresh_token": refresh_token, "access_token": access_token}
    #
    # response = user.update_user(collection, response_user.inserted_id, data_to_update)
    # print("CHECK11")
    pass


# TODO: Delete?
def create_update_list(internal_update=None):
    fields_to_updates = {}

    for key, value in request.args.items():
        fields_to_updates["key"] = value

    return fields_to_updates


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

# TODO: Handling error returns
# TODO: Grab user/pass from the environment variables (config.cfg file?)

import os

from flask import Flask, request
from flask_pymongo import PyMongo

from src.seed.seeder import seed
from src.users.models import *


# app initialization
from src.messages.models import Message

app = Flask(__name__)

# mongoDB configuration & initialization
app.config['MONGO_DBNAME'] = 'messages'

# Determining environment
isProduction = False if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == "development" else True

#  TODO: Grab user/pass from the environment variables (config.cfg file?)
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
print("collection: ", collection)

""" For testing """
# print("messages: ", collection.messages.find_one({"_id": ObjectId("61755a66e6493ae18fe77cdb")}))
# exit(0)


message_schema = {'sender': 'Yariv', 'receiver': 'Nikol', 'message': 'Hello there!', 'subject': 'Welcome',
                  'created_at': '13.10.12'}


#  Home page
@app.route("/")
def hello_world():
    return "Messaging System - RESTful API!"


#  Home page
@app.route("/seed", methods=['POST'])
def seed_db():
    seed(collection)
    return "SEED"


# Get all unread messages for specific user
@app.route('/read-all-messages', methods=['GET'])
def read_all_messages():
    """
    Query all messages (per user)
    :return: all messages for a specific user as a JSON file
    """

    # TODO: Get from request param's and use them to filter message list. (e.g. to get unread messages only)
    try:
        messages = Message.get_all_messages(collection)
        return Response(json.dumps([message for message in messages], default=json_util.default),
                        mimetype="application/json")

    except Exception as e:
        print("Error: ", e)
        return e


# Get only one message by id
@app.route('/read-message/<string:messageId>', methods=['GET'])
def read_message(messageId):
    """
    Query message where the `id` field equal messageId
    :param messageId: message identification number
    :return: Details of one message
    """
    updated_message = None
    try:
        message = Message.get_message(collection, messageId)
    except Exception as e:
        return e

    if message is not None:
        # Message found

        if message["is_read"] is False:
            is_read = {"_id": ObjectId(messageId)}, {"$set": {"is_read": True}}

            try:
                response = Message.update_message(collection, is_read)
                return Response(json.dumps(response, default=json_util.default), mimetype="application/json")

            except Exception as e:
                return {
                    "status_code": 500,
                    "message": str(e)
                }

        return Response(json.dumps(message, default=json_util.default), mimetype="application/json")

    else:
        # Message not found
        return Response("Message not found!", mimetype="application/json")


# Delete message (as owner or as receiver)
@app.route('/delete-message/<string:messageId>', methods=['DELETE'])
def delete_message(messageId):
    # Query message
    # TODO: Fix return statment + status
    # TODO: If message not found -> return correct message
    try:
        Message.delete(collection, messageId)
        return 'Deleting succeeded'

    except Exception as e:
        return e


# Write message
@app.route('/write-messages', methods=['POST'])
def write_messages():
    # Get param & create the Message object
    message = Message(request.args['sender'],
                      request.args['receiver'],
                      request.args['message'],
                      request.args['subject'])

    #  TODO: Adding to return message the id field

    try:
        # Insert message into DB
        response = message.save(collection)
        return Response(json.dumps(response.inserted_id, default=json_util.default), mimetype="application/json")

    except Exception as e:
        return e


# #######################################################################
@app.route('/create-user', methods=['POST'])
def create_user():
    # Get param & create the User object
    user = User(request.args['first_name'],
                request.args['last_name'],
                request.args['email'].lower(),
                request.args['password'])

    print("user: ", user.to_json)
    try:
        user.save(collection)
        return 'Writing Succeeded'
    except Exception as e:
        return e


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

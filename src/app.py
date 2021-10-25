# app.py
import os
import json

from bson import ObjectId, json_util
from flask import Flask, Response, request, jsonify
from flask_pymongo import PyMongo

# app initialization
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
@app.route("/api/")
def hello_world():
    return "Messaging System - RESTful API!"


# Get all unread messages for specific user
@app.route('/read-all-messages', methods=['GET'])
def read_all_messages():
    """
    Query all messages (per user)
    :return: all messages for a specific user as a JSON file
    """

    # TODO: Get from request param's and use them to filter message list. (e.g. to get unread messages only)
    params = {"isRead": None}
    req = request.args
    print("req: ", req)

    for param in req:
        print("param: ", param)

    messages = collection.messages.find()
    return Response(json.dumps([message for message in messages], default=json_util.default),
                    mimetype="application/json")


# Get all unread messages for a specific user
# TODO: Replace this endpoint by "read-all-messages" with params
@app.route('/read-unread-messages', methods=['GET'])
def read_unread_messages():
    """
     Query all unread messages
    :return
    """

    messages = collection.messages.find()
    # iterable = json.dumps([message for message in messages], default=json_util.default)
    iterable = {"_id": {"$oid": "61755a66e6493ae18fe77cdb"}, "sender": "Yariv", "receiver": "Nikol",
                "message": "Hello there!", "subject": "Welcome", "created_at": 13, "isRead": True}
    print("messages: ", messages)
    print("iterable: ", iterable)

    unread_messages = []

    for key, value in iterable.items():
        if key == "isRead" and value is True:
            unread_messages.append({"message: ": iterable["message"]})

    return Response(json.dumps([message for message in unread_messages], default=json_util.default),
                    mimetype="application/json")


# Get only one message by id
@app.route('/read-message/<string:messageId>', methods=['GET'])
def read_message(messageId):
    """
    Query message where the `id` field equal messageId
    :param messageId: message identification number
    :return: Details of one message
    """

    message = collection.messages.find_one({"_id": ObjectId(messageId)})
    return Response(json.dumps(message, default=json_util.default), mimetype="application/json")


# Delete message (as owner or as receiver)
@app.route('/delete-message/<string:messageId>', methods=['DELETE'])
def delete_message(messageId):
    message = collection.messages.delete_one({"_id": ObjectId(messageId)})
    print("Delete message: ", message)
    # return Response(json.dumps(message, default=json_util.default), mimetype="application/json")
    # TODO: Fix return statment
    return json.dumps(message)


# Write message
@app.route('/write-messages', methods=['POST'])
def write_messages():
    req_data = json.loads(request.data)

    # TODO: Create a new instance of Message object for our data
    result = collection.messages.insert_one(req_data).inserted_id
    print("result: ", result)

    # TODO: return message id to server
    return "", 204


def get_messages():
    return collection.messages.find()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

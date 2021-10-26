from flask import Blueprint
from database import database
from flask import current_app as app
from src.messages.models import Message

message_blueprint = Blueprint("messages", __name__)

# Get database collection
app = app.app_context()
app.push()

client = database.get_database()
collection = client.db
print("collection: ", collection)


# Get all messages for a specific user
@message_blueprint.route('/read-all-messages', methods=['GET'])
def read_all_messages():
    return Message().get_all_messages_by_user()


# Get all unread messages for a specific user
@message_blueprint.route('/read-unread-messages', methods=['GET'])
def read_unread_messages():
    return Message().get_all_unread_messages_by_user()


# Read message (return one message)
@message_blueprint.route('/read-message/<string:messageId>', methods=['GET'])
def read_message(messageId):
    return Message().get_message(messageId)


# Delete message (as owner or as receiver)
@message_blueprint.route('/delete-message', methods=['DELETE'])
def delete_message():
    return Message().delete()


# Write message
@message_blueprint.route('/write-message', methods=['POST'])
def write_message():
    return Message().set_message()

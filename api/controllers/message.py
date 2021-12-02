from bson import ObjectId
from flask import json
from werkzeug.exceptions import BadRequestKeyError

from api.utilities import json_resp, request
from api.models.message import Message


def read_message(message_id, user_data):
    """
    Read a message.
    :param message_id: message id
    :param user_data: user details
    :return: message object as JSON
    """

    try:
        user_id = json.loads(user_data["user_id"])["$oid"]
        message = Message.get_message(message_id)

        # Message found & it belong to user
        if message is not None:
            if message["sender_id"] == user_id:
                update_is_read_flag([message])
                return json_resp(message, 200)
            return json_resp("Forbidden!", 403)
        return json_resp("Message not exist!", 404)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def read_all_messages(user_data):
    """
    Read all messages OR all unread messages.
    :param user_data: user details
    :return: messages as JSON
    """
    try:
        user_id = json.loads(user_data["user_id"])["$oid"]
        is_read = request.args.get('only_unread')

        if is_read == 'False' or is_read == 'false':
            messages = Message.get_all_messages(user_id)
        elif is_read == 'True' or is_read == 'true':
            messages = Message.get_unread_messages(user_id)
        else:
            raise ValueError("Invalid parameter. only_unread parameter should be True or False.")

        if messages is not None:
            update_is_read_flag(messages)
            return json_resp([message for message in messages], 200)
        return json_resp([], 404)

    except BadRequestKeyError as e:
        return json_resp({"message": "Missing parameter", "exception": str(e)}, 400)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def delete_message(message_id, user_data):
    """
    Delete a message.
    :param message_id: message id
    :param user_data: user details
    :return: the number of deleted messages
    """
    try:
        user_id = json.loads(user_data["user_id"])["$oid"]
        message = Message.get_message(message_id)

        if message is not None and message["sender_id"] == user_id:
            # Message found & message belong to user
            response = Message.delete(message_id)
            return json_resp(response.deleted_count, 200)
        else:
            return json_resp("Message not found!", 404)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def write_message(user_data, message):
    """
    Create & send a message.
    :param user_data: user details
    :param message: user message
    :return: message id
    """
    try:
        user_id = json.loads(user_data["user_id"])["$oid"]
        message_obj = Message(user_id,
                              message['sender'],
                              message['receiver'],
                              message['subject'],
                              message['message'])

        return json_resp(message_obj.save().inserted_id, 201)

    except (BadRequestKeyError, IndexError) as e:
        return json_resp({"message": "Missing parameter", "exception": str(e)}, 400)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def update_is_read_flag(messages):
    """
   Update is_read flag
   :param messages: message
   :return: db response
   """
    response = []

    for message in messages:
        if not message["is_read"]:
            is_read = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
            response.append(Message.update(is_read))
        return

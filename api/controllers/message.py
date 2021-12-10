from bson import ObjectId
from flask import json
from werkzeug.exceptions import BadRequestKeyError
from http import HTTPStatus

from api.errors.errors import APIError
from api.utilities import json_resp, request
from api.models.message import Message


def read_message(message_id, user_data):
    """
    Read a message.
    :param message_id: message id
    :param user_data: user details
    :return: message object as JSON
    """
    user_id = json.loads(user_data["user_id"])["$oid"]
    message = Message.get_message(message_id)

    if message is None:
        raise APIError("Message not exist!", HTTPStatus.NOT_FOUND)

    if message["sender_id"] != user_id:
        raise APIError("Forbidden!", HTTPStatus.FORBIDDEN)

    update_is_read_flag([message])
    return json_resp(message, 200)


def read_all_messages(user_data):
    """
    Read all messages OR all unread messages.
    :param user_data: user details
    :return: messages as JSON
    """
    user_id = json.loads(user_data["user_id"])["$oid"]
    is_read = request.args.get('only_unread')

    if is_read == 'False' or is_read == 'false':
        messages = Message.get_all_messages(user_id)
    elif is_read == 'True' or is_read == 'true':
        messages = Message.get_unread_messages(user_id)
    else:
        raise APIError("Invalid parameter. only_unread parameter should be True or False.", HTTPStatus.BAD_REQUEST)

    if messages is None:
        return json_resp([], HTTPStatus.NOT_FOUND)

    update_is_read_flag(messages)
    return json_resp([message for message in messages], HTTPStatus.OK)


def delete_message(message_id, user_data):
    """
    Delete a message.
    :param message_id: message id
    :param user_data: user details
    :return: the number of deleted messages
    """
    user_id = json.loads(user_data["user_id"])["$oid"]
    message = Message.get_message(message_id)

    if message is None or message["sender_id"] != user_id:
        raise APIError("Forbidden!", HTTPStatus.FORBIDDEN)

    response = Message.delete(message_id)
    return json_resp(response.deleted_count, 200)


def write_message(user_data, message):
    """
    Create & send a message.
    :param user_data: user details
    :param message: user message
    :return: message id
    """
    user_id = json.loads(user_data["user_id"])["$oid"]
    message_obj = Message(user_id,
                          message['sender'],
                          message['receiver'],
                          message['subject'],
                          message['message'])

    return json_resp(message_obj.save().inserted_id, 201)


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

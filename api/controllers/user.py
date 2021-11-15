from bson import ObjectId, json_util
from flask import request, json
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from api import tools, auth
from api.models.message import Message
from api.models.user import User


def write(collection, user, sender_id):
    """
    Create & send a message to a user.
    """
    message = Message(sender_id,
                      request.args['sender'],
                      request.args['receiver'],
                      request.args['subject'],
                      request.args['message'])
    user.temp_messages.append(message)
    return user.send_message(collection)


def read(collection, user, message_id, user_id):
    """
    Read a message.
    :param collection: db collection
    :param user: user object
    :param message_id: message id
    :param user_id: user id
    :return: message object as JSON
    """

    try:
        message = user.read_message(collection, message_id)
        user.temp_messages.append([message])

        # Message found & it belong to user
        if message is not None and message["sender_id"] == ObjectId(user_id):
            user.update_is_read_flag(collection)
            return tools.JsonResp(message, 200)
        return tools.JsonResp("Forbidden", 403)

    except Exception as e:
        return tools.JsonResp(str(e), 500)


def read_all(collection, user, user_id, only_unread):
    """
    Read all messages OR all unread messages.
    :param collection: db collection
    :param user: user object
    :param user_id: user id
    :param only_unread: boolean flag
    :return: messages as JSON
    """
    try:
        if only_unread == 'False' or only_unread == 'false':
            only_unread = False
        elif only_unread == 'True' or only_unread == 'true':
            only_unread = True
        else:
            raise Exception("Invalid parameter")

        messages = user.read_messages(collection, user_id, only_unread)
        user.temp_messages.append(messages)

        if messages is not None:
            user.update_is_read_flag(collection)
            return tools.JsonResp([message for message in messages], 200)
        return tools.JsonResp([], 404)

    except Exception as e:
        return tools.JsonResp(str(e), 500)


def delete(collection, user, message_id, user_id):
    """
    Delete a message.
    :param collection: db collection
    :param user: user object
    :param message_id: message id
    :param user_id: user id
    :return: the number of deleted messages
    """
    try:
        message = user.read_message(collection, message_id)

        if message is not None and message["sender_id"] == ObjectId(user_id):
            # Message found & message belong to user
            response = user.delete_message(collection, message_id, user_id)
            return tools.JsonResp(response.deleted_count, 200)
        else:
            # Message not found
            return tools.JsonResp("Message not found!", 404)

    except Exception as e:
        return tools.JsonResp(str(e), 500)


def login(collection):
    """
    Login a user.
    :param collection: db collection
    :return: user details as JSON
    """
    login_details = {"email": request.args['email'].lower(),
                     "password": request.args['password']}

    user_response = User.find_user(collection, {"email": login_details["email"]})

    if user_response:
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

            # create a new token object in the tokens collection
            return User.login(collection, user_response, access_token, refresh_token)
        return tools.JsonResp({"message": "Invalid user credentials"}, 403)
    return tools.JsonResp({"message": "Invalid user credentials"}, 403)

from flask import json
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from werkzeug.exceptions import BadRequestKeyError
from api.utilities import *
from api.models.message import Message
from api.models.user import User
from api.utilities import split_data


def signup(collection):
    """
    Getting request data & creating user object
    :param collection: db collection
    :return: user object as JSON
    """
    try:
        data = split_data(request.get_data(as_text=True).split('&'))

        user = User(data['first_name'],
                    data['last_name'],
                    data['email'].lower(),
                    data['password'])

        return User.set_user(collection, user)

    except BadRequestKeyError as e:
        return json_resp({"message": "Missing parameter", "exception": str(e)}, 400)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def write(collection, sender_id):
    """
    Create & send a message to a user.
    """
    try:
        data = split_data(request.get_data(as_text=True).split('&'))

        message = Message(sender_id,
                          data['sender'],
                          data['receiver'],
                          data['subject'],
                          data['message'])

        return User.send_message(collection, message)

    except BadRequestKeyError as e:
        return json_resp({"message": "Missing parameter", "exception": str(e)}, 400)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def read(collection, message_id, user_id):
    """
    Read a message.
    :param collection: db collection
    :param message_id: message id
    :param user_id: user id
    :return: message object as JSON
    """

    try:
        message = User.read_message(collection, message_id)

        # Message found & it belong to user
        if message is not None and message["sender_id"] == user_id:
            User.update_is_read_flag(collection, [message])
            return json_resp(message, 200)
        return json_resp("Forbidden", 403)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def read_all(collection, user_id, only_unread):
    """
    Read all messages OR all unread messages.
    :param collection: db collection
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

        messages = User.read_messages(collection, user_id, only_unread)

        if messages is not None:
            User.update_is_read_flag(collection, messages)
            return json_resp([message for message in messages], 200)
        return json_resp([], 404)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def delete(collection, message_id, user_id):
    """
    Delete a message.
    :param collection: db collection
    :param message_id: message id
    :param user_id: user id
    :return: the number of deleted messages
    """
    try:
        message = User.read_message(collection, message_id)

        if message is not None and message["sender_id"] == user_id:
            # Message found & message belong to user
            response = User.delete_message(collection, message_id)
            return json_resp(response.deleted_count, 200)
        else:
            # Message not found
            return json_resp("Message not found!", 404)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def login(collection):
    """
    Login a user.
    :param collection: db collection
    :return: user details as JSON
    """
    try:
        user_login_details = split_data(request.get_data(as_text=True).split('&'))
        user_response = User.find_user(collection, {"email": user_login_details["email"]})

        if user_response and pbkdf2_sha256.verify(user_login_details["password"], user_response["password"]):
            """
            Check:
            - if user exists
            - if the password in the database is correct hash of the password
            """

            user_id = json.dumps(user_response['_id'], default=json_util.default)

            access_token = encode_access_token(user_id, user_response["email"])
            refresh_token = encode_refresh_token(user_id, user_response["email"])

            response = {
                'status': 'success',
                'message': 'Successfully registered.',
                "access_token": access_token,
                "refresh_token": refresh_token
            }

            return json_resp(response, 200)
        return json_resp({"message": "Invalid user credentials"}, 403)

    except BadRequestKeyError as e:
        return json_resp({"message": "Missing " + str(e.args[-1]), "exception": str(e)}, 400)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def logout():
    """
    Logout a user.
    :return: user details as JSON
    """
    pass
    # try:
    #     access_token = request.headers['Authorization'].split()[1]
    #     refresh_token = request.headers['Refresh-Token']
    #
    #     if utilities.is_valid_token(access_token):
    #         utilities.revoke_token(access_token)
    #         utilities.revoke_token(refresh_token)
    #         return json_resp({"message": "Successfully logged out"}, 200)
    #     return json_resp({"message": "Invalid token"}, 403)
    #
    # except Exception as e:
    #     return json_resp({"message": "Server error", "exception": str(e)}, 500)

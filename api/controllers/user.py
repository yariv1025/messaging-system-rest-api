from flask import json
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from werkzeug.exceptions import BadRequestKeyError
from api.utilities import *
from api.models.user import User
from api.utilities import valid_email


def signup(user_data):
    """
    Getting request data & creating user object
    :param user_data: user details
    :return: user object as JSON
    """
    try:
        if not valid_email(user_data['email'].lower()):
            raise ValueError("Invalid email address")

        user = User(user_data['first_name'],
                    user_data['last_name'],
                    user_data['email'].lower(),
                    user_data['password'])

        return User.set_user(user)

    except BadRequestKeyError as e:
        return json_resp({"message": "Missing parameter", "exception": str(e)}, 400)

    except Exception as e:
        return json_resp({"message": "Error", "exception": str(e)}, 500)


def login(user_data):
    """
    Login a user.
    :param user_data: user details
    :return: user details as JSON
    """
    try:
        if not valid_email(user_data["email"]):
            raise ValueError("Invalid email address.")

        user_response = User.find_user({"email": user_data["email"]})

        if user_response and pbkdf2_sha256.verify(user_data["password"], user_response["password"]):
            # check if user exists & if the password in the database is correct hash of the password
            user_id = json.dumps(user_response['_id'], default=json_util.default)
            access_token = encode_access_token(user_id, user_response["email"])
            refresh_token = encode_refresh_token(user_id, user_response["email"])

            response = {
                'status': 'success',
                'message': 'Successfully registered.',
                "access_token": access_token,
                "refresh": refresh_token
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

    try:
        access_token = request.headers['Authorization'].split()[1]

    except (BadRequestKeyError, Exception) as e:
        return json_resp({"message": "Error", "exception": str(e)}, 400)

    blocklist.add(access_token)
    return json_resp({"message": "Successfully logged out"}, 200)

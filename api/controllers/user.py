from flask import json
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from http import HTTPStatus

from api.errors.errors import APIError
from api.database.blocklist import blocklist
from api.utilities import json_resp, json_util, encode_access_token, encode_refresh_token, request
from api.models.user import User


def signup(user_data):
    """
    Getting request data & creating user object
    :param user_data: user details
    :return: user object as JSON
    """
    user = User(user_data['first_name'],
                user_data['last_name'],
                user_data['email'].lower(),
                user_data['password'])

    return User.set_user(user)


def login(user_data):
    """
    Login a user.
    :param user_data: user details
    :return: user details as JSON
    """
    user_response = User.find_user({"email": user_data["email"]})

    if not (user_response and pbkdf2_sha256.verify(user_data["password"], user_response["password"])):
        raise APIError("Invalid user credentials", HTTPStatus.FORBIDDEN)

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

    return json_resp(response, HTTPStatus.OK)


def logout(access_token):
    """
    Logout a user.
    :return: user details as JSON
    """
    blocklist.add(access_token)
    return json_resp({"message": "Successfully logged out"}, HTTPStatus.OK)

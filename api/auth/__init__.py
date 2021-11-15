import datetime
import config

from flask import request, Blueprint
from functools import wraps
from jose import jwt
from api import tools
from api.database.db import DataBase as db
from api.models.users import User
from api.tools import JsonResp

auth_blueprint = Blueprint("auth", __name__)
conf = config.Config()


def authorize_user(func):
    """
    Extension of code on an existing function.
    The authorize_user decorator performs authentication and then returns to the original function
    :param func: Another function
    :return: original func(user_id) with user id as arg
    """

    # Authorization
    def wrapper(**kwargs):
        collection = db.get_instance()
        access_token = request.headers['Authorization'].split()[1]
        token = collection.tokens.find_one({"access_token": access_token})

        if token:
            user_schema = collection.users.find_one(token["user_id"])
            user = User.get_user_instance(user_schema)
            if kwargs:
                return func(user, token["user_id"], kwargs)
            return func(user, token["user_id"])

        else:
            return tools.JsonResp("Unauthorized access", 401)

    # Change wrapper name to prevent AssertionError when
    # I tried to wrap more than one function with the decorator
    wrapper.__name__ = func.__name__
    return wrapper


def token_required(f):
    # Auth Decorator
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = request.headers.get('AccessToken')

        try:
            data = jwt.decode(access_token, conf.SECRET_KEY)
        except Exception as e:
            return JsonResp({"message": "Token is invalid", "exception": str(e)}, 401)

        return f(*args, **kwargs)

    return decorated


def encodeAccessToken(user_id, email):
    access_token = jwt.encode({
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # The token will expire in 15 minutes
    }, conf.SECRET_KEY, algorithm="HS256")
    # }, app.config["SECRET_KEY"], algorithm="HS256")

    return access_token


def encodeRefreshToken(user_id, email):
    """
    Encode refresh token
    :param user_id: user id
    :param email: email address
    :return: refresh token
    """
    refresh_token = jwt.encode({
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(weeks=4)  # The token will expire in 4 weeks
    }, conf.SECRET_KEY, algorithm="HS256")
    # }, app.config["SECRET_KEY"], algorithm="HS256")

    return refresh_token


def refreshAccessToken(refresh_token):
    # If the refresh_token is still valid, create a new access_token and return it
    try:
        collection = db.get_instance()
        user = collection.users.find_one({"refresh_token": refresh_token}, {"_id": 0, "id": 1, "email": 1, "plan": 1})

        if user:
            decoded = jwt.decode(refresh_token, conf.SECRET_KEY)
            new_access_token = encodeAccessToken(decoded["user_id"], decoded["email"])
            result = jwt.decode(new_access_token, conf.SECRET_KEY)
            result["new_access_token"] = new_access_token
            resp = JsonResp(result, 200)
        else:
            result = {"message": "Auth refresh token has expired"}
            resp = JsonResp(result, 403)

    except Exception as e:
        resp = JsonResp({"message": "Auth refresh token has expired",
                         "error": str(e)}, 403)

    return resp

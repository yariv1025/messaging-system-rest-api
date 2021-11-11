import datetime
import config

from flask import request, Blueprint
from functools import wraps
from jose import jwt
from src.database.db import DataBase as db
from src.tools import JsonResp

auth_blueprint = Blueprint("auth", __name__)
conf = config.Config()


# Auth Decorator
def token_required(f):
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

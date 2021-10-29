from flask import current_app as app
from flask import request
from functools import wraps
from src.tools import JsonResp
from jose import jwt
import datetime


# Auth Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = request.headers.get('AccessToken')

        try:
            data = jwt.decode(access_token, app.config['SECRET_KEY'])
        except Exception as e:
            return JsonResp({"message": "Token is invalid", "exception": str(e)}, 401)

        return f(*args, **kwargs)

    return decorated


# TODO: Temporary SECRET_KEY!! -> config.cfg file needed fixing
SECRET_KEY = 'aQ70AYYoi4'


def encodeAccessToken(user_id, email):
    access_token = jwt.encode({
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # The token will expire in 15 minutes
    }, SECRET_KEY, algorithm="HS256")
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
    }, SECRET_KEY, algorithm="HS256")
    # }, app.config["SECRET_KEY"], algorithm="HS256")

    return refresh_token


def refreshAccessToken(refresh_token):
    # If the refresh_token is still valid, create a new access_token and return it
    try:
        user = app.db.users.find_one({"refresh_token": refresh_token}, {"_id": 0, "id": 1, "email": 1, "plan": 1})

        if user:
            decoded = jwt.decode(refresh_token, app.config["SECRET_KEY"])
            new_access_token = encodeAccessToken(decoded["user_id"], decoded["email"], decoded["plan"])
            result = jwt.decode(new_access_token, app.config["SECRET_KEY"])
            result["new_access_token"] = new_access_token
            resp = JsonResp(result, 200)
        else:
            result = {"message": "Auth refresh token has expired"}
            resp = JsonResp(result, 403)

    except:
        result = {"message": "Auth refresh token has expired"}
        resp = JsonResp(result, 403)

    return resp


# def authorize_user(func):
#     """
#     Extension of code on an existing function.
#     The authorize_user decorator performs authentication and then returns to the original function
#     :param func: Another function
#     :return: original func(user_id) with user id as arg
#     """
#
#     # Authorization
#     def wrap_auth_check(**kwargs):
#         access_token = request.headers['Authorization'].split()[1]
#         token = collection.tokens.find_one({"access_token": access_token})
#
#         if token:
#             return func(token["user_id"])
#         else:
#             return JsonResp("Unauthorized access", 401)
#
#     return wrap_auth_check

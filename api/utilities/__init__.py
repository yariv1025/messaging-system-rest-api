import datetime
import uuid
import json
import config

from flask import Response, request, Blueprint
from bson import json_util
from pytz import timezone, UTC
from functools import wraps
from jose import jwt

utilities_blueprint = Blueprint("utilities", __name__)
conf = config.Config()


def now_datetime_user_timezone(user_timezone):
    """
    Get current datetime in user timezone
    :param user_timezone: user timezone
    :return: current datetime in user timezone
    """
    tzone = timezone(user_timezone)
    return datetime.datetime.now(tzone)


def now_datetimeUTC():
    """
    Get current datetime in UTC
    :return: current datetime in UTC
    """
    tzone = UTC
    now = datetime.datetime.now(tzone)
    return now


def json_resp(data, status):
    """
    Return json response
    :param data: data to be returned
    :param status: status code
    :return: json response
    """
    return Response(json.dumps(data, default=json_util.default), mimetype="application/json", status=status)


def rand_id():
    """
    Generate random id
    :return: random id
    """
    rand_id = uuid.uuid4().hex
    return rand_id


def valid_email(email):
    """
    Check if the email is valid
    :param email: user email address
    :return: True or False
    """
    import re

    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
        return True
    else:
        return False


def split_data(message):
    """
    Getting data from body of request and arrange it in a dictionary
    :param message: body data (x-www-form-urlencoded)
    :return: dictionary with arranged data
    """
    message = message.split('&')
    new = []
    data = {}

    for item in message:
        new.append(item.replace("%20", " ").replace("%40", "@"))

    for item in new:
        key = item.split('=')[0]
        value = item.split('=')[1]
        data[key] = value

    return data


def authorize_required(f):
    """
    Auth decorator to check if the user is authorized
    :param f:
    :return:
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        access_token = request.headers['Authorization'].split()[1]
        try:
            claim = jwt.decode(access_token, conf.SECRET_KEY)
        except Exception as e:
            return json_resp({"message": "Token is invalid", "exception": str(e)}, 401)

        return f(claim, *args, **kwargs)

    return decorated


def encode_access_token(user_id, email):
    """
     Encode access token
    :param user_id: user id
    :param email: user email address
    :return: access token
    """
    access_token = jwt.encode({
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # The token will expire in 15 minutes
    }, conf.SECRET_KEY, algorithm="HS256")

    return access_token


def encode_refresh_token(user_id, email):
    """
    Encode refresh token
    :param user_id: user id
    :param email: user email address
    :return: refresh token
    """
    refresh_token = jwt.encode({
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(weeks=1)  # The token will expire in 4 weeks
    }, conf.SECRET_KEY, algorithm="HS256")

    return refresh_token


def refresh_access_token(refresh_token):
    """
    If the refresh_token is still valid, create a new access_token and return it
    :param refresh_token: refresh token
    :return: user details & new access token
    """
    try:
        decoded = jwt.decode(refresh_token, conf.SECRET_KEY)
        new_access_token = encode_access_token(decoded["user_id"], decoded["email"])
        result = jwt.decode(new_access_token, conf.SECRET_KEY)
        result["new_access_token"] = new_access_token
        resp = json_resp(result, 200)

    except Exception as e:
        resp = json_resp({"message": "Auth refresh token has expired",
                          "error": str(e)}, 403)

    return resp

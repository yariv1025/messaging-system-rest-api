import datetime
import uuid
import json

from flask import Response
from bson import json_util
from pytz import timezone, UTC


def now_datetime_user_timezone(user_timezone):
    tzone = timezone(user_timezone)
    return datetime.datetime.now(tzone)


def now_datetimeUTC():
    tzone = UTC
    now = datetime.datetime.now(tzone)
    return now


def Json_resp(data, status):
    return Response(json.dumps(data, default=json_util.default), mimetype="application/json", status=status)


def rand_id():
    rand_id = uuid.uuid4().hex
    return rand_id


def valid_email(email):
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
    new = []
    data = {}

    for item in message:
        new.append(item.replace("%20", " "))

    for item in new:
        key = item.split('=')[0]
        value = item.split('=')[1]
        data[key] = value

    return data

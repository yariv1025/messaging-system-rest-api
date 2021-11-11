import datetime
import uuid
import json

from flask import Response
from bson import json_util
from pytz import timezone, UTC


def nowDatetimeUserTimezone(user_timezone):
    tzone = timezone(user_timezone)
    return datetime.datetime.now(tzone)


def nowDatetimeUTC():
    tzone = UTC
    now = datetime.datetime.now(tzone)
    return now


def JsonResp(data, status):
    return Response(json.dumps(data, default=json_util.default), mimetype="application/json", status=status)


def randID():
    rand_id = uuid.uuid4().hex
    return rand_id


def validEmail(email):
    import re

    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
        return True
    else:
        return False

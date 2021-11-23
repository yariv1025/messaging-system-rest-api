from flask import request
from werkzeug.exceptions import BadRequestKeyError

from api.utilities import refresh_access_token, json_resp


def refresh_token():
    """
    Refresh access token
    :return: new access token
    """
    try:
        refresh_token = request.get_data(as_text=True).split('&')[1].split('=')[1]
        return refresh_access_token(refresh_token)

    except BadRequestKeyError as e:
        return json_resp({"message": "Missing " + str(e.args[-1]), "exception": str(e)}, 400)

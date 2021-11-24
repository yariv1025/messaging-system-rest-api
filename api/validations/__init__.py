import json
from functools import wraps

from cerberus import schema_registry, Validator
from cerberus.errors import ValidationError
from flask import jsonify, request

from api.utilities import json_resp, split_data


def get_blueprint_schema(schema_name, desired_format):
    """
    Get the schema
    :param schema_name: schema file name
    :param desired_format: our desired format of schema
    :return: schema
    """
    try:
        path = './validations/' + schema_name + '.json'
        with open(path) as f:
            schema = json.load(f)
            desired_schema = schema[desired_format]

    except (IOError, EOFError, FileNotFoundError) as e:
        return "Error. {}".format(e.args[-1])

    return desired_schema


def validate_request(schema_name, desired_format):
    """
    Validating data request
    :param schema_name: schema file name
    :param desired_format: our desired format of schema
    :return: True if valid, False if not
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            try:
                raw_data = request.get_data(as_text=True)
                data = split_data(raw_data)
                schema = get_blueprint_schema(schema_name, desired_format)[0]
                v = Validator()

                if v.validate(data, schema):
                    return f(*args, data)
                else:
                    return json_resp({"Validation error": str(v.errors)}, 400)

            except BaseException as e:
                return json_resp({"ValidationError": str(e)}, 400)

        return wrapper

    return decorator
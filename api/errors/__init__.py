import traceback

from flask import jsonify
from http import HTTPStatus

from api.errors.errors import APIError


def register_error_handlers(app):
    """
    Register error handlers for the application.
    :param app: Flask application
    """

    @app.errorhandler(APIError)
    def handle_exception(err):
        """
        Return custom JSON when Exception or its children are raised
        :param err: Error object
        :return: Custom JSON response
        """
        response = {
            "code": err.status_code,
            "message": err.message,
            "payload": err.payload if app.config["DEBUG"] else "",
            "stack_trace": err.traceback if app.config["DEBUG"] else "",
        }

        return jsonify(response), err.status_code

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    @app.errorhandler(Exception)
    def handle_exception(err):
        """
        Return custom JSON when Exception or its children are raised
        :param err: Error object
        :return: Custom JSON response
        """
        response = {
            "error": f"error type: {type(err)}, error message:{str(err)}",
            "traceback": traceback.format_exc() if app.config["DEBUG"] else "",
        }

        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def handle_exception(err):
        """
        Return custom JSON when Exception or its children are raised
        :param err: Error object
        :return: Custom JSON response
        """
        response = {"error": f"error type: {type(err)}, error message:{str(err)}"}
        return jsonify(response), HTTPStatus.NOT_FOUND

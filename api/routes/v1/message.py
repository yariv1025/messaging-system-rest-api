from flask import Blueprint

from api.controllers.message import read_all_messages, read_message, delete_message, write_message
from api.validations import validate_request
from api.utilities import authorize_required

message_blueprint = Blueprint('message', __name__)


@message_blueprint.route('/messages', methods=['GET'])
@authorize_required
def get_messages(user_data):
    """
    Get all read messages / unread messages
    Postman exam: WEB_ROUTE/messages?only_unread=True
    :param user_data: user details
    :return: all messages for a specific user
    """
    return read_all_messages(user_data)


@message_blueprint.route('/messages/<string:messageId>', methods=['GET'])
@authorize_required
def get_single_message(user_data, **kwargs):
    """
    Get message by id
    Postman exam: WEB_ROUTE/messages/MESSAGE_ID_FROM_MONGO_DB
    :param user_data: user details
    :return: Details of one message
    """
    return read_message(kwargs["messageId"], user_data)


@message_blueprint.route('/messages/<string:messageId>', methods=['DELETE'])
@authorize_required
def delete(user_data, **kwargs):
    """
    Delete specific message by id
    Postman exam: WEB_ROUTE/messages/MESSAGE_ID_FROM_MONGO_DB
    :param user_data: data details
    :return: response / feedback
    """
    return delete_message(kwargs["messageId"], user_data)


@message_blueprint.route('/messages', methods=['POST'])
@authorize_required
@validate_request("message", "create")
def set_message(user_data, message):
    """
    Post message
    Postman exam: WEB_ROUTE/messages
    :param user_data: user details
    :param message: user message
    :return: message id
    """
    return write_message(user_data, message)

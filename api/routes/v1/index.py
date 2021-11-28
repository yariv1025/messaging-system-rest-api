from flask import Blueprint

homepage_blueprint = Blueprint("homepage", __name__)


@homepage_blueprint.route('/')
def home_page():
    """
    Home page
    :return: message response
    """
    return "Messaging System - REST API!"


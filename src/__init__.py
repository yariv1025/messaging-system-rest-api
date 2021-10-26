# import os
# from flask import Flask
# from flask_pymongo import PyMongo
# from src.tools import JsonResp
#
# # Import Routes
# from src.Temporary.routes import user_blueprint
# from src.messages.routes import message_blueprint
#
#
# def create_app():
#     """
#     Create messaging system app
#     :return app
#     """
#
#     # Flask Config
#     app = Flask(__name__)
#     app.app_context().push()
#
#     # Register Blueprints
#     app.register_blueprint(user_blueprint, url_prefix="/user")
#     app.register_blueprint(message_blueprint, url_prefix="/message")
#
#     @app.route("/")
#     def home_page():
#         return JsonResp({"status": "Messaging System Online - RESTful API!"}, 200)
#
#     return app

import json

from bson import ObjectId, json_util
from flask import Response
from passlib.hash import pbkdf2_sha256
from src import tools


class User:

    def __init__(self, first_name, last_name, email, password):
        """
        Initialize User object
        :param first_name (string): first name
        :param last_name (string): last name
        :param email (string): email
        :param password (integer): password
        """
        self.defaults = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": pbkdf2_sha256.encrypt(password, rounds=20000, salt_size=16),
            "date_created": tools.nowDatetimeUTC(),
            "last_login": tools.nowDatetimeUTC()
        }

    def get_user(self):
        """
        :return: user instance
        """
        return self.defaults.copy()

    def update_user(self, userId, to_update):
        """
        Update user details
        :param userId: Mongo id
        :param to_update: A dictionary of {param_to_update: new_data}
        :return:
        """
        # # TODO: Change userId to mongo id
        # user = collection.Temporary.find_one({"_id": ObjectId(userId)})
        # updated_user = None
        #
        # if user:
        #     # User found --> update fields
        #     updated_user = collection.Temporary.find_one_and_update({"_id": ObjectId(userId)},
        #                                                                   {"$set": {param_to_update: new_data}})
        #     return Response(json.dumps(user, default=json_util.default), mimetype="application/json")
        #
        # else:
        #     # User not found
        #     return Response("User not found - update failed!", mimetype="application/json")
        pass

    def to_json(self):
        """
       :return: JSON representation
       """
        return self.defaults.copy()

    def get_all_messages(self, only_unread_messages=False, from_income=False, from_outcome=False):
        """
        Get all messages from income_messages / outcome_messages.
        :param only_unread_messages: True for unread messages, False for all messages
        :param from_income:
        :param from_outcome:
        :return:
        """
        pass

    def send_message(self):
        pass

    def receive_message(self):
        pass

    def delete_message(self):
        pass

    def save(self, collection):
        return collection.users.insert_one(self.to_json())


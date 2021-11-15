import json

from bson import ObjectId, json_util
from flask import Response, request
from passlib.hash import pbkdf2_sha256
from api import tools, auth
from api.models.messages import Message


class User:

    def __init__(self, first_name, last_name, email, password):
        """
        Initialize User object
        :param first_name: first name
        :param last_name: last name
        :param email: email
        :param password: password
        """
        self.temp_messages = []
        self.defaults = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email.lower(),
            "password": pbkdf2_sha256.encrypt(password, rounds=20000, salt_size=16),
            "date_created": tools.nowDatetimeUTC(),
            "last_login": tools.nowDatetimeUTC()
        }

    def send_message(self, collection):
        """
        Sending message to user
        :param collection: db collection
        :return: response - message id
        """
        try:
            # Insert message into DB
            message = self.temp_messages.pop()
            response = message.save(collection)
            return tools.JsonResp(response.inserted_id, 200)

        except Exception as e:
            return {"error": str(e)}, 500

    def read_messages(self, collection, user_id, only_unread):
        """
        Reading all user messages || Unread user messages
        :param collection: db collection
        :param user_id: user id
        :param only_unread: flag
        :return: All user messages
        """
        try:
            if only_unread:
                return Message.get_unread_messages(collection, user_id)
            else:
                return Message.get_all_messages(collection, user_id)

        except Exception as e:
            return {"error": str(e)}, 500

    def read_message(self, collection, messageId):
        """
        Find and return single message
        :param collection: db collection
        :param messageId: message id
        :return: single message
        """
        try:
            return Message.get_message(collection, messageId)

        except Exception as e:
            return {"error": str(e)}, 500

    def delete_message(self, collection, messageId, user_id):
        """
        Delete one message by id
        :param collection: db collection
        :param messageId: message id
        :param user_id: message user_id
        :return: response / feedback
        """

        try:
            return Message.delete(collection, messageId)

        except Exception as e:
            return {"error": str(e)}, 500

    def save_user(self, collection):
        """
        Saving user into db
        :param collection: db collection
        :return:
        """
        try:
            return collection.users.insert_one(self.get_user_as_json())

        except Exception as e:
            return {"error": str(e)}, 500

    def create_user(self, collection):
        """
        Create a new user
        :param collection: db collection
        :return: user id
        """
        try:
            is_exists = self.is_exists(collection)
            if not is_exists:
                response = self.save_user(collection)
                return tools.JsonResp(response.inserted_id, 200)
            return is_exists

        except Exception as e:
            return {"error": str(e)}, 500

    def is_exists(self, collection):
        """
        Checking if the user already exists
        :param collection: db collection
        :return: user id
        """

        try:
            if tools.validEmail(self.defaults["email"]):
                user_response = collection.users.find_one({"email": self.defaults["email"].lower()})

                if user_response:
                    return tools.JsonResp("User already exists", 409)
                else:
                    return False

        except Exception as e:
            return {"error": str(e)}, 500

    def get_user_as_json(self):
        """
        :return: user instance
        """
        return self.defaults.copy()

    def update_is_read_flag(self, collection):
        """
        Update is_read flag
        :param collection: db collection
        :return: db response
        """
        response = []
        messages = self.temp_messages.pop()

        for message in messages:
            if not message["is_read"]:
                is_read = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
                response.append(Message.update_message(collection, is_read))

    @staticmethod
    def get_user_instance(user_schema):
        return User(user_schema["first_name"],
                    user_schema["last_name"],
                    user_schema["email"],
                    user_schema["password"])

    @staticmethod
    def find_user(collection, email_login_details):
        """
        Find user by email
        :param collection: db collection
        :param email_login_details: email
        :return: user instance / False if user not found
        """
        try:
            user_response = collection.users.find_one(email_login_details)
            if user_response:
                return user_response
            return False

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def login(collection, user_response, access_token, refresh_token):
        """
        User login
        :param collection: db collection
        :param user_response: user instance
        :param access_token: access token
        :param refresh_token: refresh token
        :return: user details
        """
        try:

            collection.tokens.update_many({"user_id": ObjectId(user_response['_id'])},
                                          {"$set": {"access_token": access_token,
                                                    "refresh_token": refresh_token,
                                                    "last_login": tools.nowDatetimeUTC()
                                                    }}, upsert=True)

            resp = tools.JsonResp({
                "id": user_response["_id"],
                "email": user_response["email"],
                "first_name": user_response["first_name"],
                "last_name": user_response["last_name"],
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200)

            return resp



        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def update_user(collection, userId, new_data):
        """
        Update user details
        :param collection: db collection
        :param userId: Mongo id
        :param new_data: New data
        :return: db response
        """

        try:
            user = collection.users.find_one({"_id": ObjectId(userId)})

            if user:
                # if user found --> updating fields
                return collection.users.find_one_and_update({"_id": userId}, {"$set": new_data}, upsert=True)

            else:
                # User not found
                return Response("User not found - update failed!", mimetype="application/json")

        except Exception as e:
            return {"error": str(e)}, 500

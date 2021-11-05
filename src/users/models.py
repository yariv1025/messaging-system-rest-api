import json

from bson import ObjectId
from flask import Response, request
from passlib.hash import pbkdf2_sha256

from src import tools
from src.messages.models import Message


class User:

    def __init__(self, first_name, last_name, email, password):
        """
        Initialize User object
        :param first_name: first name
        :param last_name: last name
        :param email: email
        :param password: password
        """
        self.defaults = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email.lower(),
            "password": pbkdf2_sha256.encrypt(password, rounds=20000, salt_size=16),
            "date_created": tools.nowDatetimeUTC(),
            "last_login": tools.nowDatetimeUTC()
        }

    def send_message(self, collection, sender_id):
        message = Message(sender_id,
                          request.args['sender'],
                          request.args['receiver'],
                          request.args['subject'],
                          request.args['message'])

        try:
            # Insert message into DB
            response = message.save(collection)
            return tools.JsonResp(response.inserted_id, 200)

        except Exception as e:
            return {"error": str(e)}, 500

    def read_messages(self, collection, user_id, all_messages):
        """
        Reading all user messages || Unread user messages
        :param collection: db collection
        :param user_id: user id
        :param all_messages: flag
        :return: All user messages
        """
        try:
            messages = []
            if all_messages:
                response = Message.get_all_messages(collection, user_id)
                messages = [message for message in response]
            else:
                # Unread messages only
                response = Message.get_unread_messages(collection, user_id)
                messages = [message for message in response]

            if messages:
                response = self.update_is_read_flag(collection, messages)
                return tools.JsonResp(response, 200)

            return tools.JsonResp([], 404)

        except Exception as e:
            return {"error": str(e)}, 500

    def read_message(self, collection, messageId, user_id):
        """
        Find and return single message
        :param collection: db collection
        :param messageId: message id
        :param user_id: user id
        :return: one message
        """
        try:
            message = [Message.get_message(collection, messageId)]
            if message is not None and message[0]["sender_id"] == ObjectId(user_id):
                # Message found & message belong to user
                self.update_is_read_flag(collection, message)
                return tools.JsonResp(message[0], 200)
            return tools.JsonResp("Forbidden", 403)

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
            message = Message.get_message(collection, messageId)

            if message is not None and message["sender_id"] == ObjectId(user_id):
                # Message found & message belong to user
                response = Message.delete(collection, messageId)
                return tools.JsonResp(response.deleted_count, 200)

            else:
                # Message not found
                return tools.JsonResp("Message not found!", 404)

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

    def get_user_as_json(self):
        """
        :return: user instance
        """
        return self.defaults.copy()

    @staticmethod
    def get_user_instance(user_schema):
        return User(user_schema["first_name"],
                    user_schema["last_name"],
                    user_schema["email"],
                    user_schema["password"])

    def update_is_read_flag(self, collection, messages):
        """
        Update is_read flag
        :param collection: db collection
        :param messages: user messages
        :return: db response
        """
        response = []
        for message in messages:
            if not message["is_read"]:
                is_read = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
                response.append(Message.update_message(collection, is_read))
        return messages

    def create_user(self, collection):
        """
        Create a new user
        :param collection: db collection
        :return: user id
        """

        try:
            # Looking for user
            user_response = collection.users.find_one({"email": self.defaults["email"].lower()})

            if tools.validEmail(self.defaults["email"]) and user_response is None:

                response = self.save_user(collection)
                return tools.JsonResp(response.inserted_id, 200)

            else:
                return {"message": "There's already an account with this email address",
                        "error": "email_exists"
                        }, 409

        except Exception as e:
            return {"error": str(e)}, 500

    def login(self):
        pass

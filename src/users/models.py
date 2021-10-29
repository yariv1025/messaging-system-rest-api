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

    @staticmethod
    def send_message(collection, sender_id):
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

    @staticmethod
    def read_all_messages(collection, user_id):
        """
        Reading all user messages
        :param collection: db collection
        :param user_id: user id
        :return: All user messages
        """

        try:
            messages = Message.get_all_messages(collection, user_id)
            # Update is_read flag
            response = []
            for message in messages:
                fields = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
                response.append(Message.update_message(collection, fields))

            # return tools.JsonResp([message for message in messages], 200)
            return tools.JsonResp(response, 200)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def read_unread_messages(collection, user_id):
        """
        Reading all unread user messages
        :param collection: db collection
        :param user_id: user id
        :return: All user unread messages
        """

        try:
            messages = Message.get_unread_messages(collection, user_id)
            # Update is_read flag
            response = []
            for message in messages:
                is_read = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
                response.append(Message.update_message(collection, is_read))

            return tools.JsonResp(response, 200)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def read_message(collection, messageId, user_id):
        """
        Find and return message
        :param collection: db collection
        :param messageId: message id
        :param user_id: user id
        :return: one message
        """
        try:
            message = Message.get_message(collection, messageId)

            if message is not None:
                if message["sender_id"] == ObjectId(user_id):
                    # Message found & message belong to user

                    if message["is_read"] is False:
                        # Update is_read flag
                        is_read = {"_id": ObjectId(messageId)}, {"$set": {"is_read": True}}
                        response = Message.update_message(collection, is_read)
                        return tools.JsonResp(response, 200)

                    # Returning the message without updating
                    return tools.JsonResp(message, 200)

                else:
                    # Message dose not belong to user
                    return tools.JsonResp("Unauthorized access", 401)

        except Exception as e:
            return {"error": str(e)}, 500

        else:
            # Message not found
            return tools.JsonResp("Message not found!", 404)

    @staticmethod
    def delete_message(collection, messageId, user_id):
        """
        Delete one message by id
        :param collection: db collection
        :param messageId: message id
        :param user_id: message user_id
        :return: response / feedback
        """

        try:
            message = Message.get_message(collection, messageId)

            if message is not None:
                if message["sender_id"] == ObjectId(user_id):
                    # Message found & message belong to user

                    response = Message.delete(collection, messageId)
                    return tools.JsonResp(response.deleted_count, 401)

                else:
                    return tools.JsonResp("Unauthorized access", 401)

            else:
                # Message not found
                # return Response("Message not found!", mimetype="application/json")
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
        :return:
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
            return collection.users.insert_one(self.get_user())

        except Exception as e:
            return {"error": str(e)}, 500

    def get_user(self):
        """
        :return: user instance
        """
        return self.defaults.copy()

    @staticmethod
    def update_is_read_flag(collection, messageId):
        """
        :param collection: db collection
        :param messageId: message id
        :return: mongo response
        """
        # # Update is_read flag
        # is_read = {"_id": ObjectId(messageId)}, {"$set": {"is_read": True}}
        # response = Message.update_message(collection, is_read)
        # return tools.JsonResp(response, 200)
        pass

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

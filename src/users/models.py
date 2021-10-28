import json

from bson import json_util, ObjectId
from flask import Response, request
from passlib.hash import pbkdf2_sha256
from pymongo import ReturnDocument

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
            "email": email,
            "password": pbkdf2_sha256.encrypt(password, rounds=20000, salt_size=16),
            "date_created": tools.nowDatetimeUTC(),
            "last_login": tools.nowDatetimeUTC()
        }

    @staticmethod
    def send_message(collection):
        message = Message(request.args['sender'],
                          request.args['receiver'],
                          request.args['message'],
                          request.args['subject'])

        try:
            # Insert message into DB
            response = message.save(collection)
            return tools.JsonResp(response.inserted_id, 200)

        except Exception as e:
            return e

    @staticmethod
    def read_all_messages(collection):
        """
        Read all user messages
        :param collection: db collection
        :return: All user messages
        """

        # TODO: Get from request param's and use them to filter message list. (e.g. to get unread messages only)
        # TODO: Update is_read field for all messages
        messages = Message.get_all_messages(collection)
        return tools.JsonResp([message for message in messages], 200)

    @staticmethod
    def read_message(collection, messageId):
        """
        Find and return message
        :param collection: db collection
        :param messageId: message id
        :return: one message
        """

        message = Message.get_message(collection, messageId)

        if message is not None:
            # Message found

            if message["is_read"] is False:
                # Update is_read flag
                is_read = {"_id": ObjectId(messageId)}, {"$set": {"is_read": True}}
                response = Message.update_message(collection, is_read)
                return tools.JsonResp(response, 200)

            # Returning the message without updating
            return tools.JsonResp(message, 200)

        else:
            # Message not found
            return Response("Message not found!", mimetype="application/json")

    @staticmethod
    def delete_message(collection, messageId):
        """
        Delete one message by id
        :param collection: db collection
        :param messageId: message id
        :return: response / feedback
        """
        response = Message.delete(collection, messageId)
        return {
            "status_code": 200,
            "Amount of deleted message:": json.dumps(response.deleted_count, default=json_util.default)
        }

    @staticmethod
    def update_user(collection, userId, new_data):
        """
        Update user details
        :param collection: db collection
        :param userId: Mongo id
        :param new_data: New data
        :return:
        """

        user = collection.users.find_one({"_id": ObjectId(userId)})

        if user:
            # User found --> update fields
            # return collection.users.find_one_and_update({"_id": ObjectId(user["_id"])}, {"$set": new_data})
            return collection.users.find_one_and_update({"_id": userId}, {"$set": new_data}, upsert=True)

        else:
            # User not found
            return Response("User not found - update failed!", mimetype="application/json")

    def save(self, collection):
        """
        Saving user into db
        :param collection: db collection
        :return:
        """
        return collection.users.insert_one(self.get_user())

    def get_user(self):
        """
        :return: user instance
        """
        return self.defaults.copy()

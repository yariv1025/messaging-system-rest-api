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
            return e

    @staticmethod
    def read_all_messages(collection, user_id):
        """
        Reading all user messages
        :param collection: db collection
        :param user_id: user id
        :return: All user messages
        """

        # TODO: Get from request param's and use them to filter message list. (e.g. to get unread messages only)
        # TODO: Update is_read field for all messages

        messages = Message.get_all_messages(collection, user_id)
        # Update is_read flag
        response = []
        for message in messages:
            fields = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
            response.append(Message.update_message(collection, fields))

        # return tools.JsonResp([message for message in messages], 200)
        return tools.JsonResp(response, 200)

    @staticmethod
    def read_unread_messages(collection, user_id):
        """
        Reading all user unread messages
        :param collection: db collection
        :param user_id: user id
        :return: All user unread messages
        """

        messages = Message.get_unread_messages(collection, user_id)
        # Update is_read flag
        response = []
        for message in messages:
            is_read = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
            response.append(Message.update_message(collection, is_read))

        return tools.JsonResp(response, 200)

    @staticmethod
    def read_message(collection, messageId, user_id):
        """
        Find and return message
        :param collection: db collection
        :param messageId: message id
        :param user_id: user id
        :return: one message
        """

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

        else:
            # Message not found
            # return Response("Message not found!", mimetype="application/json")
            return tools.JsonResp("Message not found!", 401)

    @staticmethod
    def delete_message(collection, messageId):
        """
        Delete one message by id
        :param collection: db collection
        :param messageId: message id
        :return: response / feedback
        """
        return Message.delete(collection, messageId)

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
            # if user found --> updating fields
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

    @staticmethod
    def update_is_read_flag(collection, messageId):
        """
        TODO: For refactoring of all reading methods
        :param collection: db collection
        :param messageId: message id
        :return: mongo response
        """
        # # Update is_read flag
        # is_read = {"_id": ObjectId(messageId)}, {"$set": {"is_read": True}}
        # response = Message.update_message(collection, is_read)
        # return tools.JsonResp(response, 200)

import bson
from bson import ObjectId
from api.tools import *


class Message:

    def __init__(self, sender_id, sender_name, receiver_name, subject, message):
        """
        Initialize Message object
        :param senderId (integer): sender ID
        :param receiverId (integer): receiver ID
        :param subject (string): the subject of message
        :param message (string): message
        """
        self.defaults = {
            "sender_id": sender_id,
            "sender": sender_name,
            "receiver": receiver_name,
            "subject": subject,
            "message": message,
            "date_created": nowDatetimeUTC(),
            "is_read": False
        }

    def save(self, collection):
        """
        Saving single message into db
        :param collection: db collection
        """
        return collection.messages.insert_one(self.to_json())

    def to_json(self):
        """
        :return: JSON representation
        """
        return self.defaults.copy()

    @staticmethod
    def get_all_messages(collection, user_id):
        """
        Querying all user messages
        :param collection: db collection
        :param user_id: user id
        :return: all messages for a specific user
        """
        return list(collection.messages.find({"sender_id": ObjectId(user_id)}))

    @staticmethod
    def get_unread_messages(collection, user_id):
        """
        Querying all user unread messages from db
        :param collection: db collection
        :param user_id: user id
        :return: all unread messages for a specific user
        """
        return list(collection.messages.find({"sender_id": ObjectId(user_id), "is_read": False}))

    @staticmethod
    def get_message(collection, messageId):
        """
        Query message by messageId
        :param collection: db collection
        :param messageId: message identification number
        :return: Details of one message
        """
        return collection.messages.find_one({"_id": ObjectId(messageId)})

    @staticmethod
    def delete(collection, messageId):
        """
        Deleting message by messageId
        :param collection: db collection
        :param messageId: message id
        """
        return collection.messages.delete_one({"_id": ObjectId(messageId)})

    @staticmethod
    def update_message(collection, desired_fields):
        """
        :param collection: db collection
        :param desired_fields: key=field to update, value=data to be updated
        :return: the original message (before update)
        """
        return collection.messages.find_one_and_update(desired_fields[0], desired_fields[1])

from bson import ObjectId

from src.tools import *


class Message:

    def __init__(self, senderId, receiverId, subject, message):
        """
        Initialize Message object
        :param senderId (integer): sender ID
        :param receiverId (integer): receiver ID
        :param subject (string): the subject of message
        :param message (string): message
        """
        self.defaults = {
            "sender": senderId,
            "receiver": receiverId,
            "subject": subject,
            "message": message,
            "date_created": nowDatetimeUTC(),
            "is_read": False
        }

    @classmethod
    def get_all_messages(cls, collection):
        """
        Query all messages (per user)
        :return: all messages for a specific user as a JSON file
        """
        return collection.messages.find()

    @classmethod
    def get_message(cls, collection, messageId):
        """
        Query message where the `id` field equal to messageId
        :param collection: db collection
        :param messageId: message identification number
        :return: Details of one message
        """

        return collection.messages.find_one({"_id": ObjectId(messageId)})

    @classmethod
    def delete(cls, collection, messageId):
        """
        Delete desired message
        :param collection: db collection
        :param messageId: message id
        """
        collection.messages.delete_one({"_id": ObjectId(messageId)})

    @staticmethod
    def update_message(collection, desired_field):
        """
        :param collection:
        :param desired_field: The field we want to update
        :param new_data: new data
        :return: the original message (before update)
        """
        return collection.messages.find_one_and_update(desired_field[0], desired_field[1])

    def save(self, collection):
        """
        Save message to db
        :param collection: db collection
        """
        return collection.messages.insert_one(self.to_json())

    def to_json(self):
        """
        :return: JSON representation
        """
        return self.defaults.copy()

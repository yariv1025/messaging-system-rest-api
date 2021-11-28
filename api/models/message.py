from bson import ObjectId

from api.database.db import DataBase
from api.utilities import now_datetimeUTC, handle_query


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
            "date_created": now_datetimeUTC(),
            "is_read": False
        }

    def save(self):
        """
        Saving single message into db
        """
        return handle_query(DataBase.save_item(self.to_json(), "messages"))

    def to_json(self):
        """
        :return: JSON representation
        """
        return self.defaults.copy()

    @staticmethod
    def get_all_messages(user_id):
        """
        Calling to the db to get all messages for a specific user
        :param user_id: user id
        :return: all messages for a specific user
        """
        return handle_query(list(DataBase.get_all_items({"sender_id": user_id}, "messages")))

    @staticmethod
    def get_unread_messages(user_id):
        """
        Calling to the db to get all unread messages for a specific user
        :param user_id: user id
        :return: all unread messages for a specific user
        """
        return handle_query(list(DataBase.get_all_items({"sender_id": user_id, "is_read": False}, "messages")))

    @staticmethod
    def get_message(message_id):
        """
        Calling to the db to get message by messageId
        :param message_id: message identification number
        :return: Details of one message
        """
        return handle_query(DataBase.get_item_by_filter({"_id": ObjectId(message_id)}, "messages"))

    @staticmethod
    def delete(messageId):
        """
        Calling to the db to delete message by messageId
        :param messageId: message id
        """
        return handle_query(DataBase.delete_item({"_id": ObjectId(messageId)}, "messages"))

    @staticmethod
    def update(desired_fields):
        """
        Calling to the db to update desired fields in a message
        :param desired_fields: key=field to update, value=data to be updated
        :return: the original message (before update)
        """
        return handle_query(DataBase.update_item(desired_fields, "messages"))
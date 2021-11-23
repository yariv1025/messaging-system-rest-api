from bson import ObjectId
from passlib.hash import pbkdf2_sha256
from api.utilities import *
from api.models.message import Message


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
            "date_created": now_datetimeUTC(),
            "last_login": now_datetimeUTC()
        }

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

    def is_exists(self, collection):
        """
        Checking if the user already exists
        :param collection: db collection
        :return: user id
        """

        try:
            user_response = collection.users.find_one({"email": self.defaults["email"].lower()})

            if user_response:
                return json_resp("User already exists", 409)
            else:
                return False

        except Exception as e:
            return {"error": str(e)}, 500

    def get_user_as_json(self):
        """
        :return: user instance
        """
        return self.defaults.copy()

    @staticmethod
    def send_message(collection, message):
        """
        Sending message to user
        :param collection: db collection
        :param message: message
        :return: response - message id
        """
        try:
            response = message.save(collection)
            return json_resp(response.inserted_id, 200)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def read_messages(collection, user_id, only_unread):
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

    @staticmethod
    def read_message(collection, messageId):
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

    @staticmethod
    def delete_message(collection, messageId):
        """
        Delete one message by id
        :param collection: db collection
        :param messageId: message id
        :return: response / feedback
        """

        try:
            return Message.delete(collection, messageId)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def update_is_read_flag(collection, messages):
        """
        Update is_read flag
        :param collection: db collection
        :param messages: message
        :return: db response
        """
        response = []

        for message in messages:
            if not message["is_read"]:
                is_read = {"_id": ObjectId(message["_id"])}, {"$set": {"is_read": True}}
                response.append(Message.update_message(collection, is_read))

    @staticmethod
    def set_user(collection, user):
        """
        Create a new user
        :param collection: db collection
        :param user: user object
        :return: user id
        """
        try:
            is_exists = user.is_exists(collection)

            if not is_exists:
                response = user.save_user(collection)
                return json_resp(response.inserted_id, 200)
            return is_exists

        except Exception as e:
            return {"error": str(e)}, 500

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

from passlib.hash import pbkdf2_sha256
from api.utilities import *
from api.database.db import DataBase


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

    def save_user(self):
        """
        Saving user into db
        :return: user id
        """
        try:
            return DataBase.save_item(self.get_user_as_json(), "users")

        except Exception as e:
            return {"error": str(e)}, 500

    def is_exists(self):
        """
        Checking if the user already exists
        :return: user id
        """

        try:
            user_response = DataBase.get_item({"email": self.defaults["email"].lower()}, "users")
            return json_resp("User already exists", 409) if user_response else False

        except Exception as e:
            return {"error": str(e)}, 500

    def get_user_as_json(self):
        """
        :return: user instance
        """
        return self.defaults.copy()

    @staticmethod
    def set_user(user):
        """
        Create a new user
        :param user: user object
        :return: user id
        """
        try:
            is_exists = user.is_exists()

            if not is_exists:
                response = user.save_user()
                return json_resp(response.inserted_id, 201)
            return is_exists

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_user_instance(user_schema):
        user = User(user_schema["first_name"],
                    user_schema["last_name"],
                    user_schema["email"],
                    user_schema["password"])
        return user

    @staticmethod
    def find_user(email_login_details):
        """
        Find user by email
        :param email_login_details: email
        :return: user instance / False if user not found
        """
        try:
            user_response = DataBase.get_item_by_filter(email_login_details, "users")
            return user_response if user_response else False

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def update_user(userId, new_data):
        """
        Update user details
        :param userId: Mongo id
        :param new_data: New data
        :return: original user document
        """
        try:
            updated_user = DataBase.update_item([{"_id": userId}, {"$set": new_data}], "users")
            return json_resp(updated_user, 200) if updated_user else json_resp("User not found", 404)

            # user = DataBase.get_item_by_filter({"_id": ObjectId(userId)}, "users")
            #
            # if user:
            #     return DataBase.update_item([{"_id": userId}, {"$set": new_data}], "users")
            #
            # else:
            #     return Response("User not found - update failed!", mimetype="application/json")

        except Exception as e:
            return {"error": str(e)}, 500

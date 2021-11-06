import json

from src.models.users import User
from src.models.messages import Message


def seed(collection):
    """
    Create users() return user id list
    create_messages() takes that list and insert each id to the correct message object
    :param collection:
    :return:
    """
    user_id = []
    user_id = create_users(collection)
    create_messages(collection, user_id)


def create_users(collection):
    """
    Seeding users data to users collection
    :param collection: db collection
    """

    try:
        user_id = []
        with open('./src/seed/INIT_DATA.json') as f:
            init_collections = json.load(f)
            users = init_collections["users"]

        # Create user object for each user in users list and save_user there id in user_id list
        for user in users:
            user = User(user["first_name"], user["last_name"], user["email"], user["password"])
            response = user.save_user(collection)
            user_id.append(response.inserted_id)

        f.close()
        return user_id

    except (IOError, EOFError) as e:
        print("Error. {}".format(e.args[-1]))


def create_messages(collection, user_id):
    """
    Seeding messages data to messages collection
    :param collection: db collection
    :param user_id: users id's list
    """
    try:
        with open('./src/seed/INIT_DATA.json') as f:
            init_collections = json.load(f)
            messages = init_collections["messages"]

        for message in messages:
            id_number = user_id.pop()
            message = Message(id_number, message["sender"], message["receiver"], message["subject"], message["message"])
            message.save(collection)

        f.close()

    except (IOError, EOFError) as e:
        print("Error. {}".format(e.args[-1]))

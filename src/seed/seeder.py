import json
from src.users.models import User
from src.messages.models import Message


def seed(collection):
    create_users(collection)
    create_messages(collection)


def create_users(collection):
    with open('./src/seed/INIT_DATA.json') as f:
        collections = json.load(f)
        users = collections["users"]

    for user in users:
        user = User(user["first_name"], user["last_name"], user["email"], user["password"])
        user.save(collection)

    f.close()


def create_messages(collection):
    with open('./src/seed/INIT_DATA.json') as f:
        collections = json.load(f)
        messages = collections["messages"]

    for message in messages:
        message = Message(message["sender"], message["receiver"], message["subject"], message["message"])
        message.save(collection)

    f.close()
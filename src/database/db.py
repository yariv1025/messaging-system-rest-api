from flask_pymongo import PyMongo


class DataBase:
    client = None

    @staticmethod
    def get_instance(app=None):
        if DataBase.client is None and app is not None:
            DataBase.client = PyMongo(app)
        elif app is None and DataBase.client is None:
            raise Exception("No app provided")

        return DataBase.client.db

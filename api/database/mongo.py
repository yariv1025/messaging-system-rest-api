from flask_pymongo import PyMongo


class DataBase:
    client = None

    def __init__(self, app):
        """
        Initialize the database
        :param app: Flask app
        """
        DataBase.client = PyMongo(app)

    @staticmethod
    def get_instance(app=None):
        """
        Singleton - Get the instance of the database
        :param app: Flask app
        :return: Database instance
        """
        if DataBase.client is None and app is not None:
            DataBase(app)
        elif app is None and DataBase.client is None:
            raise Exception("No app provided")

        return DataBase.client.db

    @staticmethod
    def save_item(item, collection_name):
        """
        Save an item in the database
        :param item: item to save
        :param collection_name: db collection
        :return: item id
        """
        try:
            return DataBase.get_instance().get_collection(collection_name).insert_one(item)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_item(item, collection_name):
        """
        Get an item from the database
        :param item: item to get
        :param collection_name: db collection
        :return: item
        """
        try:
            return DataBase.get_instance().get_collection(collection_name).find_one(item)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def update_item(item, collection_name):
        """
        Update an item in the database
        :param item: item to update (item[0] is KEY , item[1] is VALUE)
        :param collection_name: db collection
        :return: the item before update
        """
        try:
            return DataBase.get_instance().get_collection(collection_name).find_one_and_update(item[0], item[1], upsert=True)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def delete_item(item, collection_name):
        """
        Delete an item from the database
        :param item: item to delete
        :param collection_name: db collection
        :return: A document containing: A boolean indicating if the deletion was successful & counter of deleted items
        """
        try:
            return DataBase.get_instance().get_collection(collection_name).delete_one(item)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_all_items(filters, collection_name):
        """
        Get all items from the database
        :param filters: filters to apply
        :param collection_name: db collection
        :return: items
        """
        try:
            return DataBase.get_instance().get_collection(collection_name).find(filters)

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_item_by_filter(filters, collection_name):
        """
        Get an item from the database
        :param filters: filters to apply
        :param collection_name: db collection
        :return: item
        """
        try:
            return DataBase.get_instance().get_collection(collection_name).find_one(filters)

        except Exception as e:
            return {"error": str(e)}, 500

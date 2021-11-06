import os


class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = 'aQ70AYYoi4'
    MONGO_DBNAME = "massaging_system"
    MONGO_PASS = os.getenv('MONGO_PASS')
    MONGO_USER = os.getenv('MONGO_USER')
    DB_URI = os.getenv('DB_URI')
    MONGO_URI = f'mongodb+srv://{MONGO_USER}:{MONGO_PASS}{DB_URI}'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

import os


class Config(object):
    DEBUG = False
    TESTING = False

    PORT = 5000
    HOST = '127.0.0.1'
    SECRET_KEY = os.getenv('SECRET_KEY')
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


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

exportConfig = config[os.getenv('FLASK_ENV', 'default')]


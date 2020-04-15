import os

# Default config
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///game.db'

class DevConfig(object):
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'dev key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///game.db'

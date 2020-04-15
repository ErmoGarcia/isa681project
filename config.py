import os

DEBUG = True
TESTING = True
SECRET_KEY = os.urandom(24)
SQLALCHEMY_DATABASE_URI = 'sqlite:///game.db'

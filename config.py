import os

DEBUG = False
TESTING = False
SECRET_KEY = '\xce\xe2?\x91F\x81\n\x1b\x86\xc7\xd5\x9b\xe62S\x07B\rF\x88)\x80H\xe3'
# SECRET_KEY = os.urandom(24)
SQLALCHEMY_DATABASE_URI = 'sqlite:///game.db'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

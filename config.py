import secrets

class Config(object):
    SECRET_KEY = secrets.token_hex()
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postpass@localhost/myappdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USER_APP_NAME = "My App"
    USER_ENABLE_EMAIL = True
    USER_ENABLE_USERNAME = False
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"

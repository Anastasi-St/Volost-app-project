import secrets

class Config(object):
    SECRET_KEY = secrets.token_hex()
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postpass@localhost/myappdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    pswrd = 'f185f5e6e0fd51c0e51d1d38d42810a04e3e757b0dbe73e297c6c24798fc2f4e'
    #SQLALCHEMY_DATABASE_URI = 'postgresql://akrcemgftgutgk:'+pswrd+'@ec2-52-44-13-158.compute-1.amazonaws.com:5432/d7l5tct4hj9k4i'

    USER_APP_NAME = "Volost court protocols"
    USER_ENABLE_EMAIL = True
    USER_ENABLE_USERNAME = False
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
    USER_ENABLE_REGISTER = False
    USER_ENABLE_FORGOT_PASSWORD = False

    UPLOAD_FOLDER = 'static/images/doc_images/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
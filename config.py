from dotenv import load_dotenv
from os import environ

load_dotenv()


class Config:
    SECRET_KEY = environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROOT_URL = environ['ROOT_URL']
    MAIL_SERVER = environ['MAIL_SERVER']
    MAIL_USERNAME = environ['MAIL_USERNAME']
    MAIL_PASSWORD = environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = environ['MAIL_DEFAULT_SENDER']
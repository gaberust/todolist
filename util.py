import time
import jwt
from flask import render_template
from flask_mail import Mail, Message

from config import Config
from models import User

mail = Mail()


def create_verification_token(user: User):
    return jwt.encode({
        'sub': user.id,
        'exp': int(time.time()) + 1440  # 24 hours
    }, Config.SECRET_KEY, algorithm='HS256')


def send_verification_email(user: User):
    mail.send(
        Message(
            'Please Verify Your Email Address',
            recipients=[user.email],
            html=render_template(
                'verification_email.html',
                verification_link=f'{Config.ROOT_URL}/verify?token={create_verification_token(user)}'
            )
        )
    )
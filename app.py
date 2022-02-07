from functools import wraps

import jwt
from flask import Flask, render_template, request, g, session, redirect, url_for
import re

from config import Config
from models import db, bcrypt, User, TodoItem
from util import mail, send_verification_email

app = Flask(__name__)

with app.app_context():
    app.config.from_object(Config)
    bcrypt.init_app(app)
    db.init_app(app)
    db.create_all()
    mail.init_app(app)


@app.before_request
def populate_user():
    g.user_id = session.get('user_id')
    g.user = None
    if g.user_id:
        g.user = User.query.get(g.user_id)


def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return func


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        context = request.form.copy()
        context['username'] = context['username'].strip()
        context['email'] = context['email'].strip()
        errors = []
        if len(context['username']) > 32:
            errors.append('Username cannot be longer than 32 characters.')
        if not context['username'].isalnum():
            errors.append('Username must be alphanumeric.')
        if User.find_by_email_or_username(context['username']):
            errors.append('That username already exists.')
        if len(context['email']) > 100:
            errors.append('Email cannot be longer than 100 characters.')
        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', context['email']):
            errors.append('Invalid email address.')
        if User.find_by_email_or_username(context['email']):
            errors.append('That email already exists.')
        if len(context['password']) < 12:
            errors.append('Password must be at least 12 characters long.')
        if context['password'] != context['confirm_password']:
            errors.append('Passwords do not match.')
        if errors:
            return render_template('register.html', errors=errors, **context)

        user = User()
        user.username = context['username']
        user.email = context['email']
        user.set_password(context['password'])

        db.session.add(user)
        db.session.commit()
        db.session.flush()
        db.session.refresh(user)

        send_verification_email(user)

        return render_template('register.html', success=True)


@app.route('/verify', methods=['GET'])
def verify():
    try:
        payload = jwt.decode(request.args['token'], Config.SECRET_KEY, algorithms=['HS256'])
        if user := User.query.get(payload['sub']):
            user.email_verified = True
            db.session.add(user)
            db.session.commit()
            db.session.flush()
        return render_template('')
    except jwt.ExpiredSignatureError:
        return render_template('')
    except jwt.InvalidTokenError:
        return render_template('')


if __name__ == '__main__':
    app.run()

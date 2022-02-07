from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    query: db.Query

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    verified = db.Column(db.Boolean, default=False)

    todo_items = db.relationship('TodoItem', backref='user')

    @hybrid_property
    def username_lower(self):
        return self.username.lower()

    @username_lower.expression
    def username_lower(self):
        return db.func.lower(self.username)

    @hybrid_property
    def email_lower(self):
        return self.email.lower()

    @email_lower.expression
    def email_lower(self):
        return db.func.lower(self.email)

    @staticmethod
    def find_by_email_or_username(identifier: str):
        return User.query.filter((User.email_lower == db.func.lower(identifier)) |
                                 (User.username_lower == db.func.lower(identifier))).first()

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class TodoItem(db.Model):
    __tablename__ = 'todos'

    query: db.Query

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1024), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
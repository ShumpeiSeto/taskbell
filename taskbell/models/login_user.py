from taskbell import db, login_manager
from flask_login import UserMixin
from datetime import datetime


class User(UserMixin, db.Model):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(255))
    created_time = db.Column(db.Datetime, nullable=False, default=datetime.now)
    updated_time = db.Column(
        db.Datetime, nullable=False, default=datetime.now, onupdate=datetime.now
    )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

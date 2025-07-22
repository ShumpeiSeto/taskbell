from taskbell import db
from datetime import datetime


class Tasks(db.Model):
    def __init__(
        self,
        title=None,
        deadline=None,
        is_completed=None,
        user_id=None,
        importance=None,
    ):
        self.title = title
        self.deadline = deadline
        self.is_completed = is_completed
        self.user_id = user_id
        self.importance = importance

    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    deadline = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    importance = db.Column(db.Integer, nullable=False)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_time = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    # user_id = db.relationship("User", backref="tasks")

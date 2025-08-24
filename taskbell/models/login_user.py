from taskbell import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# from flask_login import login_manager


class User(UserMixin, db.Model):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.user_id = None
        self.nc_v_mode = 0
        self.c_v_mode = 0
        self.dl_time = 0

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_time = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    nc_v_mode = db.Column(db.Integer)
    c_v_mode = db.Column(db.Integer)
    dl_time = db.Column(db.Integer, default=0)
    task_id = db.relationship("Tasks", backref="users")

    # is_authenticated をoverrideし、username, passwordチェックをしていたが、
    # どうやら継承元UserMinxinのis_authenticatedの方で比較してくれているみたいだ

    def is_authenticated(self, input_username, input_password):
        if self.username == input_username and check_password_hash(
            self.password, input_password
        ):
            return True
        else:
            return False

    # def is_authenticated(self):
    #     return True

    # def is_active(self):
    #     return True

    # def is_annonymous(self):
    #     pass

    def get_id(self):
        return int(self.id)


# sessionに保存されているuser_idからユーザーオブジェクトを返す
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

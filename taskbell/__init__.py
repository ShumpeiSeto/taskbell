from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# from .models.login_user import User

print("__init__.pyがじっこうされました")
app = Flask(__name__)
print("appがつくられました")
app.config.from_object("taskbell.config")
app.secret_key = "abcdefghijk"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
# # sessionに保存されているuser_idからユーザーオブジェクトを返す
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# taskbell内の__init__ではviewsは定義されてなかったけど、フォルダ内のviews.pyを発見した
# views.pyを実行する
from taskbell import views

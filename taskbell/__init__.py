from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate 

# from .models.login_user import User

print("__init__.pyがじっこうされました")
app = Flask(__name__)
print("appがつくられました")
# config file別途作成している

app.config.from_object("taskbell.config")
app.secret_key = "abcdefghijk"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Migration 設定
migrate = Migrate(app, db)

# taskbell内の__init__ではviewsは定義されてなかったけど、フォルダ内のviews.pyを発見した
# views.pyを実行する
from taskbell import views

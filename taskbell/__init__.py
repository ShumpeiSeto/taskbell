# coding: utf-8
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import datetime

# slack定期実行のた目のテスト用
# from apscheduler.schedulers.background import BackgroundScheduler

# def post_to_slack():
#     print('定期実行なう！')

print("__init__.pyがじっこうされました")
app = Flask(__name__)
print("appがつくられました")
# config file別途作成している

app.config.from_object("taskbell.config")
app.secret_key = "abcdefghijk"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# dbできた後でモデルをインポート
from taskbell.models.add_task import Tasks
from taskbell.models.login_user import User


# 言語設定のためのカスタムフィルター
@app.template_filter("add_weekday")
def str_add_weekday(date):
    today = datetime.date.today()
    tommorrow = today + datetime.timedelta(days=1)
    yesterday = today + datetime.timedelta(days=-1)
    if today == date.date():
        return "今日"
    elif tommorrow == date.date():
        return "明日"
    elif yesterday == date.date():
        return "昨日"

    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekdays[date.weekday()]
    return f"{date.strftime('%m/%d')}({weekday})"


# 重要度から漢字重要度を出すフィルター
@app.template_filter("convert_importance")
def str_convert_importance(num_importance):
    importances = ["★", "★★", "★★★"]
    importance = importances[num_importance]
    return importance

# 定期実行のためのテスト
# scheduler = BackgroundScheduler()
# scheduler.add_job(post_to_slack, 'interval', seconds=60)
# scheduler.start()
# print('定期実行が開始しました')

# Migration 設定
migrate = Migrate(app, db)

# views.pyを実行する
from taskbell import views

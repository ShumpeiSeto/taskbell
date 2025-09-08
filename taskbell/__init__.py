# coding: utf-8
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import datetime

# slack通知定期実行のためのテスト用２
import schedule
import time
import threading


# スケジュール変数
schedule_user = {}
scheduler_thread = None

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


# 重要度を星で表現するフィルター
@app.template_filter("convert_importance")
def str_convert_importance(num_importance):
    importances = ["★", "★★", "★★★"]
    importance = importances[num_importance]
    return importance


scheduler_thread = None


def schedule_runner():
    """スケジューラを実行し続ける関数"""
    with app.app_context():
        print("=== スケジューラー開始 ===")
        while True:
            current_time = datetime.datetime.now()
            print(f"[{current_time}] スケジュールをチェック中...")
            schedule.run_pending()
            time.sleep(60)


def init_scheduler():
    """アプリ起動時にスケジューラを初期化"""
    global scheduler_thread

    if scheduler_thread is None or not scheduler_thread.is_alive():
        # 既存ユーザーのスケジュールを復元
        restore_user_schedules()

        # スケジューラスレッドを開始
        scheduler_thread = threading.Thread(target=schedule_runner, daemon=True)
        scheduler_thread.start()
        print("✅ スケジューラが起動しました")


def restore_user_schedules():
    from .models.login_user import User
    from .views import slack_notify

    """データベースからユーザーのスケジュール設定を復元"""
    try:
        users = User.query.filter(
            User.morning_time != None,
            (User.slack_url != None) | (User.email != None),
        ).all()

        for user in users:
            if user.morning_time:
                morning_time_str = user.morning_time.strftime("%H:%M")
                schedule.every().days.at(morning_time_str).do(slack_notify, user.id)
                print(
                    f"📅 ユーザー {user.username} のスケジュール復元: {morning_time_str}"
                )

    except Exception as e:
        print(f"⚠️ スケジュール復元エラー: {e}")


# Migration 設定
migrate = Migrate(app, db)

# views.pyを実行する
from taskbell import views

# アプリ起動時にスケジューラ起動
init_scheduler()

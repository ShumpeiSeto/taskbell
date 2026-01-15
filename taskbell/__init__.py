# coding: utf-8
import os
import datetime
import time
import threading
import schedule
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_mail import Mail

# 1. グローバル・インスタンス（他のファイルから import するもの）
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# メール
mail = Mail()

# スケジュール管理用の変数
schedule_user = {}
scheduler_thread = None


def create_app():
    load_dotenv()
    app = Flask(__name__)

    # 2. アプリの設定
    app.config.from_object("taskbell.config")
    app.secret_key = os.environ.get("SECRET_KEY")

    # メール設定
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")

    # 3. 拡張機能の初期化（インスタンスとアプリを紐付ける）
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # 4. カスタムフィルターの登録
    @app.template_filter("add_weekday")
    def str_add_weekday(date):
        if not date:
            return ""
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today + datetime.timedelta(days=-1)

        if today == date.date():
            return "今日"
        elif tomorrow == date.date():
            return "明日"
        elif yesterday == date.date():
            return "昨日"

        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[date.weekday()]
        return f"{date.strftime('%m/%d')}({weekday})"

    @app.template_filter("convert_importance")
    def str_convert_importance(num_importance):
        importances = ["★", "★★", "★★★"]
        return (
            importances[num_importance]
            if 0 <= num_importance < len(importances)
            else ""
        )

    # 5. Blueprint の登録
    # ここで views フォルダ内の各ファイルを読み込む
    from taskbell.views.auth import auth_bp
    from taskbell.views.tasks import tasks_bp

    # from taskbell.views.tasks import tasks_bp # tasks.pyを作ったらコメント解除

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    # 6. スケジューラの起動（アプリコンテキストを渡す）
    init_scheduler(app)

    return app


# --- スケジューラ関連の関数 ---


def schedule_runner(app):
    """スケジューラを実行し続けるスレッド用関数"""
    # スレッド内で DB 操作などをするために app_context を使う
    with app.app_context():
        print("=== スケジューラー開始 ===")
        while True:
            schedule.run_pending()
            time.sleep(60)


def init_scheduler(app):
    """アプリ起動時にスケジューラを初期化"""
    global scheduler_thread

    if scheduler_thread is None or not scheduler_thread.is_alive():
        # 既存ユーザーのスケジュールを復元
        restore_user_schedules(app)

        # スレッドに app を渡して開始
        scheduler_thread = threading.Thread(
            target=schedule_runner, args=(app,), daemon=True
        )
        scheduler_thread.start()
        print("✅ スケジューラが起動しました")


def restore_user_schedules(app):
    """データベースからユーザーのスケジュール設定を復元"""
    with app.app_context():
        try:
            # 循環参照を防ぐため関数内でインポート
            from taskbell.models.login_user import User

            # slack_notify も views フォルダ等へ移動した場所からインポート
            # from taskbell.views.utils import slack_notify
            from taskbell.views.tasks import slack_notify

            users = User.query.filter(
                User.morning_time != None,
                (User.slack_url != None) | (User.email != None),
            ).all()

            for user in users:
                if user.morning_time:
                    morning_time_str = user.morning_time.strftime("%H:%M")
                    # schedule に user.id を渡してジョブを登録
                    schedule.every().days.at(morning_time_str).do(slack_notify, user.id)
                    print(
                        f"📅 ユーザー {user.username} のスケジュール復元: {morning_time_str}"
                    )

        except Exception as e:
            print(f"⚠️ スケジュール復元エラー: {e}")

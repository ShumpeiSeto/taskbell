from flask import render_template, request, redirect, Flask, flash, session, jsonify
from taskbell import app, db, scheduler_thread
from .models.add_task import Tasks
from .models.login_user import User
from .postToSlack import post_to_slack
from datetime import datetime, timedelta
import json

from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

# from flask_sqlalchemy import desc
from flask_login import login_user, current_user, login_required, logout_user
import slackweb

# slack定期実行のた目のテスト用
from apscheduler.schedulers.background import BackgroundScheduler

# slack通知定期実行のためのテスト用２
import schedule
from time import sleep
import time
import threading

# メール送信のため
from flask_mail import Mail, Message
from flask import current_app

# メールのための設定
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "tskb.peipei@gmail.com"
app.config["MAIL_PASSWORD"] = "jmtnwzsayqxjxkhe"
app.config["MAIL_DEFAULT_SENDER"] = "tskb.peipei@gmail.com"
mail = Mail(app)

# スケジュール変数
# schedule_user = {}
# scheduler_thread = None


def send_email_notification(limity_tasks, user):
    try:
        # タスク一覧のテキストを作成
        task_list = "\n".join(
            [
                f"・{task.title} (期限: {task.deadline.strftime('%Y/%m/%d %H:%M')})"
                for task in limity_tasks
            ]
        )

        body = f"""
こんにちは {user.username} さん、

期限切れのタスクが {len(limity_tasks)} 件あります：

{task_list}

早めの対応をお願いします。

TaskBell より
        """

        # Messageオブジェクト作成
        msg = Message(
            subject=f"【TaskBell】期限切れタスク {len(limity_tasks)} 件",
            recipients=[user.email],
            body=body,
        )

        # メール送信
        mail.send(msg)
        print(f"メール送信成功: {user.email}")
        return True

    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


# scheduleで回すためのSlack通知関数
# @app.route("/api/slack/notify", methods="POST")
# @login_required
def slack_notify(user_id):
    with app.app_context():
        try:
            user = User.query.get(user_id)
            now = datetime.now()
            limity_tasks = Tasks.query.filter(
                Tasks.deadline < now,
                Tasks.is_completed == False,
                Tasks.user_id == user_id,
            ).all()
            if len(limity_tasks) > 0:
                if user.slack_url:
                    send_to_slack2(limity_tasks, user)
                if user.email:
                    email_success = send_email_notification(limity_tasks, user)
            return True
        except Exception as e:
            print("Error:", e)


# 手動テーブル削除と作成用（テスト時）
def init_db():
    # DB作成する(一旦削除したうえで)
    db.drop_all()
    db.create_all()


# 期限日時設定関数。秒以下の扱いでエラーあるので、%Sのないものも用意
def make_deadline(dead_date, dead_time):
    s = f"{dead_date} {dead_time}"
    s_format = "%Y-%m-%d %H:%M"
    deadline = datetime.strptime(s, s_format)
    print(deadline)
    return deadline


# def make_deadline2(deadline):
#     s_format = "%Y-%m-%d %H:%M:%S"
#     result = datetime.strptime(deadline, s_format)
#     print(result)
#     return result


def make_deadline2(deadline):
    s_format = "%Y-%m-%d %H:%M:%S"
    native_dt = datetime.strptime(deadline, s_format)
    iso_string = native_dt.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    print(iso_string)
    return iso_string


def convert_dl_time(value):
    dl_time = None
    if value == 0:
        dl_time = 15
    if value == 1:
        dl_time = 30
    if value == 2:
        dl_time = 60
    return dl_time


def insert(task_obj):
    with app.app_context():
        print("==========1件登録==========")
        task = Tasks(
            title=task_obj["title"],
            deadline=task_obj["deadline"],
            is_completed=False,
            user_id=task_obj["user_id"],
            importance=task_obj["importance"],
        )
        db.session.add(task)
        db.session.commit()
        db.session.close()
    return redirect("/my_task")


def add_new_task(task_obj):
    with app.app_context():
        print("==========1件登録==========")
        task = Tasks(
            title=task_obj["title"],
            deadline=task_obj["deadline"],
            is_completed=False,
            user_id=task_obj["user_id"],
            importance=task_obj["importance"],
        )
        db.session.add(task)
        db.session.commit()
        new_task_id = task.task_id
        task_dict = {
            "task_id": task.task_id,
            "title": task.title,
            "deadline": task.deadline,
            "is_completed": task.is_completed,
            "user_id": task.user_id,
            "importance": task.importance,
        }
        db.session.close()
        return task_dict


def update(task, update_info):
    with app.app_context():
        print("==========1件更新==========")
        task.title = update_info["title"]
        task.deadline = update_info["dead_line"]
        # task.is_completed = update_info["is_completed"]
        task.importance = update_info["importance"]
        try:
            # db.session.add(task)
            db.session.merge(task)
            db.session.commit()
            print("データ更新に成功しました")
            print(
                f"更新後タスク:task_id:{task.task_id}, title:{task.title}, deadline:{task.deadline}"
            )
        except Exception as e:
            db.session.rollback()
            print(f"更新エラーしました：{e}")
        finally:
            db.session.close()
    print("更新処理がおわりました")


def delete(task_id):
    with app.app_context():
        task = Tasks.query.filter(Tasks.task_id == task_id).first()
        print("==========1件削除==========")
        try:
            db.session.delete(task)
            db.session.commit()
            print("データ削除成功しました")
        except Exception as e:
            db.session.rollback()
            print(f"削除エラーしました：{e}")
        finally:
            db.session.close()
    print("削除完了しました")


def check(task_id, task):
    with app.app_context():
        print("==========1件チェック済==========")
        task.is_completed = task.is_completed ^ 1
        try:
            # db.session.add(task)
            db.session.merge(task)
            db.session.commit()
            print(
                f"タスクステータスを変更しました:task_id:{task.task_id}, title:{task.title}, is_completed:{task.is_completed}"
            )
        except Exception as e:
            db.session.rollback()
            print(f"更新エラーしました：{e}")
        finally:
            db.session.close()
    print("チェック処理がおわりました")


def signup_user(target_user):
    with app.app_context():
        print("==========1件ユーザー登録==========")
        user = User(username=target_user["username"], password=target_user["password"])
        db.session.add(user)
        db.session.commit()
        db.session.close()
    return redirect("/")


def remove_user_schedule(user_id):
    jobs_to_remove = []
    for job in schedule.jobs:
        # job.job_funcがslack_notifyで、引数がuser_idのもののみ削除
        if (
            hasattr(job.job_func, "args")
            and len(job.job_func.args) > 0
            and job.job_func.args[0] == user_id
        ):
            jobs_to_remove.append(job)

    for job in jobs_to_remove:
        schedule.cancel_job(job)


# Error Handling
@app.errorhandler(400)
def handle_bad_request(e):
    return render_template("testtemp/error.html"), 400


@app.errorhandler(401)
def handle_unauthorized(e):
    return render_template("testtemp/error.html"), 401


@app.errorhandler(403)
def handle_forbidden(e):
    return render_template("testtemp/error.html"), 403


@app.errorhandler(404)
def handle_not_found(e):
    return render_template("testtemp/error.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("testtemp/error.html"), 500


# app オブジェにルートを登録する
@app.route("/")
def index():
    logout_user()
    session.clear()
    return render_template("testtemp/index.html")


@app.before_request
def initialize_session():
    # if "nc_mode" not in session and "c_mode" not in session:
    #     session["nc_mode"] = 0
    #     session["c_mode"] = 0
    # 30分を期限設定しておく
    if "dl_time" not in session:
        session["dl_time"] = convert_dl_time(1)
    # session.pop("_flashes", None)
    if "slack_url" not in session:
        session["slack_url"] = None
    if "email" not in session:
        session["email"] = None


@app.route("/slack_help")
@login_required
def slack_help():
    return render_template("testtemp/slack_help.html")


@app.route("/my_task")
@login_required
def my_task():
    all_tasks = Tasks.query.order_by(Tasks.deadline)
    all_tasks_desc = Tasks.query.order_by(desc(Tasks.importance), Tasks.deadline)
    if session["nc_v_mode"] == 0:
        nc_tasks = all_tasks.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 0
        )
    elif session["nc_v_mode"] == 1:
        nc_tasks = all_tasks_desc.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 0
        )

    if session["c_v_mode"] == 0:
        c_tasks = all_tasks.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 1
        )
    elif session["c_v_mode"] == 1:
        c_tasks = all_tasks_desc.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 1
        )
    # print(nc_tasks)
    # now = datetime.datetime.now()
    # limity_nctasks_list = [nc_task for nc_task in nc_tasks if nc_task['deadline'] < now]
    # if len(limity_nctasks_list) >= 1:
    #     post_to_slack("期限切れのタスクがあります")

    return render_template("testtemp/my_task.html", nc_tasks=nc_tasks, c_tasks=c_tasks)


@app.route("/my_task/sorted")
@login_required
def my_task_i_sorted():
    all_tasks = Tasks.query.order_by(desc(Tasks.importance))
    nc_tasks = all_tasks.filter(Tasks.user_id == current_user.id).filter(
        Tasks.is_completed == 0
    )
    c_tasks = all_tasks.filter(Tasks.user_id == current_user.id).filter(
        Tasks.is_completed == 1
    )
    return render_template("testtemp/my_task.html", nc_tasks=nc_tasks, c_tasks=c_tasks)


@app.route("/my_task/<int:flg>")
@login_required
def button_click(flg):
    if flg == 1:
        session["nc_v_mode"] = 1
    if flg == 2:
        session["nc_v_mode"] = 0
    if flg == 3:
        session["c_v_mode"] = 1
    if flg == 4:
        session["c_v_mode"] = 0
    return redirect("/my_task")


def schedule_runner():
    with app.app_context():
        print("=== スケジューラー開始 ===")
        while True:
            current_time = datetime.now()
            print(f"[{current_time}] スケジュールをチェック中...")
            schedule.run_pending()
            time.sleep(180)

@app.route("/api/update_sortinfo/<int:flg>", methods=["POST"])
@login_required
def update_sortInfo(flg):
    with app.app_context():
        # user = User.query.filter(User.id == current_user.id).one_or_none()
        try:
            if flg == 1:
                current_user.nc_v_mode = 1
            if flg == 2:
                current_user.nc_v_mode = 0
            if flg == 3:
                current_user.nc_v_mode = 1
            if flg == 4:
                current_user.nc_v_mode = 0
            db.session.commit()
            return jsonify(
                {
                    "status": "success",
                    "message": "ソート情報を更新しました",
                })
        except Exception as e:
            db.session.rollback()
            print(f"ソート情報更新エラーしました: {e}")
        finally:
            db.session.close()
            print(f"ソート情報処理終了しました: {e}")
            
    
    

@app.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    if request.method == "GET":
        dl_time_mode = current_user.dl_time
        slack_url = current_user.slack_url or ""
        email = current_user.email or ""

        if current_user.morning_time:
            morning_time = current_user.morning_time.strftime("%H:%M")
        else:
            morning_time = "08:00"
        # print(current_user.dl_time)
        return render_template(
            "testtemp/settings.html",
            dl_time_mode=dl_time_mode,
            slack_url=slack_url,
            email=email,
            morning_time=morning_time,
        )
    elif request.method == "POST":
        global scheduler_thread
        # dl_time => 0, 1, 2
        dl_time = int(request.form.get("dl_time"))
        slack_url = request.form.get("slack_url").strip()
        email = request.form.get("email").strip()

        morning_time_str = request.form.get("morning_time")
        morning_time = datetime.strptime(morning_time_str, "%H:%M").time()

        print(f"dl_time: {dl_time}")
        print(f"slack_url: {slack_url}")
        print(f"email: {email}")
        print(f"morning_time: {morning_time}")
        current_user.dl_time = dl_time
        current_user.email = email
        current_user.slack_url = slack_url
        current_user.morning_time = morning_time
        session["dl_time"] = convert_dl_time(dl_time)
        session["slack_url"] = slack_url
        session["email"] = email
        # session["morning_time"] = morning_time
        db.session.commit()

        # user_id = current_user.id
        # schedule_user[user_id] = {
        #     "morning_time": morning_time_str,
        #     "slack_url": slack_url,
        #     "email": email,
        # }

        # スケジュール登録してみる
        remove_user_schedule(current_user.id)
        schedule.every().days.at(morning_time_str).do(slack_notify, current_user.id)
        # デバッグ用のコードを追加
        # if scheduler_thread is None or not scheduler_thread.is_alive():
        #     scheduler_thread = threading.Thread(target=schedule_runner, daemon=True)
        #     scheduler_thread.start()
        #     print("スケジューラ開始")
        # else:
        #     print("スケジューラは動作中")
        # for job in schedule.jobs:
        #     print(f"Job: {job}, Next run: {job.next_run}")
    return redirect("/my_task")


@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    # flash message残っていることがあるため削除
    session.pop("_flashes", None)
    if request.method == "GET":
        return render_template("testtemp/new_task.html")
    elif request.method == "POST":
        title = request.form.get("title")
        dead_date = request.form.get("dead_date")
        dead_time = request.form.get("dead_time")
        deadline = make_deadline(dead_date, dead_time)
        is_completed = False
        user_id = current_user.id
        importance = request.form.get("importance")
        target_task = dict(
            title=title,
            deadline=deadline,
            is_completed=is_completed,
            user_id=user_id,
            importance=importance,
        )
        print(target_task)
        flash(f"「{title}」が登録されました")
        insert(target_task)
    return render_template("testtemp/new_task.html")


@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Tasks.query.filter(Tasks.task_id == task_id).first()
    print(task)
    if request.method == "GET":
        return render_template("testtemp/edit_task.html", task=task)
    elif request.method == "POST":
        print("更新がはじまります。")
        title = request.form.get("title")
        dead_date = request.form.get("dead_date")
        dead_time = request.form.get("dead_time")
        dead_line = make_deadline(dead_date, dead_time)
        importance = int(request.form.get("importance"))
        is_completed = False
        update_info = {
            "title": title,
            "dead_line": dead_line,
            "is_completed": is_completed,
            "importance": importance,
        }
        update(task, update_info)
    return redirect("/my_task")


# edit_task の API version
# @app.route("/api/edit_task/<int:task_id>", methods=["GET", "POST"])
# @login_required
# def api_edit_task(task_id):
#     task = Tasks.query.filter(Tasks.task_id == task_id).first()
#     if request.method == "GET":
#         pass
#     elif request.method == "POST":
#         # check(task_id, task)

#         return jsonify(
#             {
#                 "status": "success",
#                 "message": "タスクを更新しました",
#                 "task_id": task_id,
#                 "is_completed": task.is_completed,
#             }
#         )


@app.route("/api/delete_task/<int:task_id>", methods=["POST"])
@login_required
def api_delete_task(task_id):
    # データの該当タスクの削除する
    delete(task_id)
    return jsonify(
        {
            "status": "success",
            "message": "タスクを削除しました",
            "task": {
                "task_id": task_id,
            },
        }
    )


@app.route("/api/get_task/<int:task_id>", methods=["GET"])
@login_required
def api_get_task(task_id):
    with app.app_context():
        try:
            task = Tasks.query.filter(Tasks.task_id == task_id).first()
            if task:
                dead_date = task.deadline.strftime("%Y-%m-%d")
                dead_time = task.deadline.strftime("%H:%M")
                return jsonify(
                    {
                        "status": "success",
                        "task": {
                            "task_id": task.task_id,
                            "title": task.title,
                            "dead_date": dead_date,
                            "dead_time": dead_time,
                            "importance": task.importance,
                        },
                    }
                )
            else:
                return (
                    jsonify({"status": "error", "message": "タスクが見つかりません"}),
                    404,
                )
        except Exception as e:
            print("Error:", e)


@app.route("/delete_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def delete_task(task_id):
    task = Tasks.query.filter(Tasks.task_id == task_id).first()
    if request.method == "GET":
        return render_template(
            "testtemp/delete_confirm_task.html", task_id=task_id, task=task
        )
    elif request.method == "POST":
        print("削除処理がはじまります")
        delete(task_id)
    # return render_template("testtemp/delete_confirm_task.html", index=index)
    return redirect("/my_task")


@app.route("/checked/<int:task_id>")
@login_required
def check_task(task_id):
    # checked = request.form.get('task-' + str(task_id))
    task = Tasks.query.filter(Tasks.task_id == task_id).first()
    # target_task = f"task-{task_id}"
    # checked = request.form.get(target_task)
    # if checked == "on":
    print(f"{task_id}:{task}")
    check(task_id, task)
    return redirect("/my_task")


# API Versionを追加してみる
@app.route("/api/checked/<int:task_id>", methods=["POST"])
@login_required
def api_check_task(task_id):
    task = Tasks.query.filter(Tasks.task_id == task_id).first()
    check(task_id, task)
    return jsonify(
        {
            "status": "success",
            "message": "タスクを更新しました",
            "task_id": task_id,
            "is_completed": task.is_completed,
        }
    )


# API Versionを追加してみる
@app.route("/api/uncheck/<int:task_id>", methods=["POST"])
@login_required
def api_uncheck_task(task_id):
    task = Tasks.query.filter(Tasks.task_id == task_id).first()
    check(task_id, task)
    return jsonify(
        {
            "status": "success",
            "message": "タスクを未完了にしました",
            "task_id": task_id,
            "is_completed": task.is_completed,
        }
    )


# アクセスするとテーブル削除と作成
@app.route("/make_table")
def make_table():
    with app.app_context():
        init_db()
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("testtemp/login.html")
    elif request.method == "POST":
        # if current_user.is_authenticated:
        #     return render_template("testtemp/index.html", current_user=current_user)

        # ユーザーが存在するかユーザ名で検索する
        username = request.form.get("username", "").strip()
        user = User.query.filter(User.username == username).one_or_none()
        password = request.form.get("password", "").strip()
        session["nc_v_mode"] = user.nc_v_mode
        session["c_v_mode"] = user.c_v_mode
        session["dl_time"] = user.dl_time
        session["is_first_slack"] = 1
        # print(user)

        # instanceつくる
        # overrrideしていたが継承元UserMixinのものでOKだった
        if (user is not None) and (user.is_authenticated(username, password)):
            # if user.is_authenticated:
            login_user(user)
            flash("認証成しました\n")
            flash(f"あなたは{user.username}です\n")
            return redirect("/my_task")
        else:
            flash("ユーザー名とパスワードが一致していません")
            flash("もう一度入力してください")
            return redirect("/login")
    return render_template("testtemp/login.html")


@app.route("/logout")
@login_required
def logout():
    current_user.nc_v_mode = session["nc_v_mode"]
    current_user.c_v_mode = session["c_v_mode"]
    # current_user.dl_time = session["dl_time"]
    db.session.commit()
    session.clear()
    logout_user()
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("testtemp/signup.html")
    elif request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        c_password = request.form.get("conf_password", "").strip()
        target_user = dict(username=username, password=generate_password_hash(password))

        # Validation
        # データチェック
        # ユーザー存在有無を確認し重複のチェック
        match_user = User.query.filter(User.username == username).first()
        if password != c_password:
            flash("パスワードが一致していません")
            flash("もう一度入力してください")
            return redirect("/signup")
        if match_user == None:
            signup_user(target_user)
            return redirect("/login")
        else:
            flash("そのユーザー名は既に存在します")
            flash("別のユーザー名で登録してください")
            return redirect("/signup")

        # 重複するユーザーが存在する場合は赤メッセージで遷移させない
        # return redirect("/login")
    return render_template("testtemp/signup.html")


@app.route("/api/get_mytasks", methods=["GET"])
@login_required
def get_mytasks():
    with app.app_context():
        try:
            my_tasks = Tasks.query.filter(Tasks.user_id == current_user.id).all()
            print(my_tasks)
            # JSON 形式に変換
            tasks_data = []
            for task in my_tasks:
                tasks_data.append(
                    {
                        "id": task.task_id,
                        "title": task.title,
                        "deadline": task.deadline.isoformat(),
                        "format_deadline": task.deadline.strftime("%Y/%m/%d %H:%M"),
                        "importance": task.importance,
                        "username": current_user.username,
                    }
                )
            return jsonify(
                {"success": True, "data": tasks_data, "count": len(tasks_data)}
            )
        except Exception as e:
            print("Error", e)
    print("API返却処理が終わりました")


@app.route("/api/task/create", methods=["POST"])
@login_required
def create_task():
    data = request.get_json()
    data["user_id"] = current_user.id
    deadline = datetime.fromisoformat(make_deadline2(data["deadline"]))
    data["deadline"] = deadline
    print(data)
    task = add_new_task(data)
    task_response = dict(task)
    task_response["deadline"] = task["deadline"].isoformat().replace(" ", "T") + ".000Z"

    return jsonify(
        {"success": True, "data": task_response, "message": "タスクが作成されました"}
    )


@app.route("/api/task/update/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    task = Tasks.query.filter(Tasks.task_id == task_id).first()
    data = request.get_json()
    title = data["title"]
    dead_date = data["dead_date"]
    dead_time = data["dead_time"]
    importance = data["importance"]
    dead_line = make_deadline(data["dead_date"], data["dead_time"])
    importance = data["importance"]
    # 更新処理をする
    update_info = {
        "task_id": task_id,
        "title": title,
        "dead_date": dead_date,
        "dead_time": dead_time,
        "dead_line": dead_line,
        "importance": importance,
    }
    update(task, update_info)
    # dead_date = task.deadline.strftime("%Y-%m-%d")
    # dead_time = task.deadline.strftime("%H:%M")
    # update_info2 = {
    #     task_id,
    #     title,
    #     dead_date,
    #     dead_time,
    #     importance,
    # # }
    return jsonify(
        {
            "status": "success",
            "updateTask": update_info,
            "message": "タスクが更新されました",
        }
    )


@app.route("/api/tasks/limity", methods=["GET"])
@login_required
def get_limity_tasks():
    now = datetime.now()
    dl_time = session["dl_time"]
    print(dl_time)
    # target_time = datetime.now() + datetime.timedelta(minutes=int(dl_time))
    limity_tasks = Tasks.query.filter(
        Tasks.deadline < now + timedelta(minutes=dl_time),
        Tasks.is_completed == False,
        Tasks.user_id == current_user.id,
    ).all()

    # JSON 形式に変換
    tasks_data = []
    for task in limity_tasks:

        tasks_data.append(
            {
                "id": task.task_id,
                "title": task.title,
                "deadline": task.deadline.isoformat(),
                "format_deadline": task.deadline.strftime("%Y/%m/%d %H:%M"),
                "importance": task.importance,
                "username": current_user.username,
            }
        )
    return jsonify({"success": True, "data": tasks_data, "count": len(tasks_data)})


def send_to_slack(limity_tasks):
    try:
        # Slack設定
        # slack_hook_url = (
        #     "https://hooks.slack.com/services/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"
        # )
        # slack_hook_url = (session['slack_url'])
        slack_hook_url = current_user.slack_url
        slack = slackweb.Slack(url=slack_hook_url)
        attachments = []

        header_attachment = {
            "color": "#ff0000",
            "title": "⚠️期限切れタスク通知です",
            "text": f"{len(limity_tasks)}件のタスクが期限切れです",
            "mrkdwn_in": ["text"],
        }
        attachments.append(header_attachment)
        for task in limity_tasks:
            deadline = datetime.fromisoformat(task["deadline"].replace("Z", "+00:00"))
            delay_hours = int((datetime.now() - deadline).total_seconds() / 3600)
            if task.get("importance") == 2:
                color = "#ff0000"  # 赤
                emoji = "🔴"
                importance = "高"
            elif task.get("importance") == 1:
                color = "#ffa500"  # オレンジ
                emoji = "🟡"
                importance = "中"
            else:
                color = "#008000"  # 緑
                emoji = "🟢"
                importance = "低"

            task_attachment = {
                "title": f"{emoji}{task['title']}",
                # "text": f"{task['deadline']}",
                "color": color,
                "fields": [
                    {"title": "担当者", "value": f"@{task['username']}", "short": True},
                    {"title": "期限", "value": task["format_deadline"], "short": True},
                    {
                        "title": "重要度",
                        "value": f"{emoji} {importance}",
                        "short": True,
                    },
                    {
                        "title": "遅延時間",
                        "value": f"{delay_hours}時間",
                        "short": True,
                    },
                ],
                "mrkdwn_in": ["fields"],
            }
            attachments.append(task_attachment)
        text = f"期限切れタスクが{len(limity_tasks)}件あります"
        slack.notify(
            text=text,
            icon_emoji=":bell:",
            username="TaskBell Bot",
            attachments=attachments,
        )
        session["is_first_slack"] = 0
        return True
    except Exception as e:
        print(f"Slack送信エラー発生しました")
        return False
    finally:
        session["is_first_slack"] = 0


def send_to_slack2(limity_tasks, user):
    try:
        slack_hook_url = user.slack_url
        slack = slackweb.Slack(url=slack_hook_url)
        attachments = []

        header_attachment = {
            "color": "#ff0000",
            "title": "⚠️期限切れタスク通知です",
            "text": f"{len(limity_tasks)}件のタスクが期限切れです",
            "mrkdwn_in": ["text"],
        }
        attachments.append(header_attachment)
        for task in limity_tasks:
            # deadline = datetime.fromisoformat(task["deadline"])
            delay_hours = int((datetime.now() - task.deadline).total_seconds() / 3600)
            if task.importance == 2:
                color = "#ff0000"  # 赤
                emoji = "🔴"
                importance = "高"
            elif task.importance == 1:
                color = "#ffa500"  # オレンジ
                emoji = "🟡"
                importance = "中"
            else:
                color = "#008000"  # 緑
                emoji = "🟢"
                importance = "低"

            task_attachment = {
                "title": f"{emoji}{task.title}",
                # "text": f"{task['deadline']}",
                "color": color,
                "fields": [
                    {
                        "title": "担当者",
                        "value": f"@{user.username}",
                        "short": True,
                    },
                    {
                        "title": "期限",
                        "value": task.deadline.strftime("%Y/%m/%d %H:%M"),
                        "short": True,
                    },
                    {
                        "title": "重要度",
                        "value": f"{emoji} {importance}",
                        "short": True,
                    },
                    {
                        "title": "遅延時間",
                        "value": f"{delay_hours}時間",
                        "short": True,
                    },
                ],
                "mrkdwn_in": ["fields"],
            }
            attachments.append(task_attachment)
        text = f"期限切れタスクが{len(limity_tasks)}件あります"
        slack.notify(
            text=text,
            icon_emoji=":bell:",
            username="TaskBell Bot",
            attachments=attachments,
        )
        print("Slack通知に成功しました！")
        return True
    except Exception as e:
        print(f"Slack送信エラー詳細: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


# JSの方では、定期実行させるJSを動かしている
# 1. 期限切れタスクを取りに行く（その際にチェッしている形式はJSON)
# 2. そのJSONをオブジェクトにする
# 3. そのオブジェクトでHTTPリクエストを作る
# 4. それを下記の notify_limit_tasksでSlackに投げる


# slackに送信するメソッド
@app.route("/api/slack/notify_limit", methods=["POST"])
@login_required
def notify_limit_tasks():
    data = request.get_json()
    limity_tasks = data.get("limity_tasks", [])
    if not limity_tasks:
        return jsonify({"success": True, "message": "期限切れタスクはありません"})
    if current_user.slack_url:
        success = send_to_slack(limity_tasks)
        if success:
            print("Slack通知送信完了")
            return jsonify({"success": True, "message": "Slack通知完了"})
        else:
            print("Slack通知送信失敗")
            return jsonify({"success": False, "message": "Slack通知失敗"})
    else:
        print("SlackURLが設定されていません")
        return jsonify({"success": False, "message": "SlackURL未設定による通知失敗"})


# flask の session確認用テスト
@app.route("/api/get_session", methods=["GET"])
@login_required
def get_session():
    sessionData = {
        "c_v_mode": session["c_v_mode"],
        "nc_v_mode": session["nc_v_mode"],
        "dl_time": session["dl_time"],
    }
    if len(sessionData) >= 1:
        return jsonify(
            {
                "success": True,
                "message": "session受取成功しました",
                "session": sessionData,
            }
        )
    else:
        print("session受取に失敗しました")
        return jsonify(
            {
                "success": False,
                "message": "session受取失敗しました",
            }
        )

from flask import render_template, request, redirect, Flask, flash, session, jsonify
from taskbell import app, db
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


# 手動テーブル削除と作成用（テスト時）
def init_db():
    # DB作成する(一旦削除したうえで)
    db.drop_all()
    db.create_all()


# Slack設定
slack_hook_url = (
    "https://hooks.slack.com/services/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"
)
slack = slackweb.Slack(url=slack_hook_url)


# 期限日時設定関数。秒以下の扱いでエラーあるので、%Sのないものも用意
def make_deadline(dead_date, dead_time):
    s = f"{dead_date} {dead_time}"
    s_format = "%Y-%m-%d %H:%M"
    deadline = datetime.strptime(s, s_format)
    print(deadline)
    return deadline


# def make_deadline2(dead_date, dead_time):
#     s = f"{dead_date} {dead_time}"
#     s_format = "%Y-%m-%d %H:%M:%S"
#     deadline = datetime.datetime.strptime(s, s_format)
#     print(deadline)
#     return deadline


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


def update(task, update_info):
    with app.app_context():
        print("==========1件更新==========")
        task.title = update_info["title"]
        task.deadline = update_info["dead_line"]
        task.is_completed = update_info["is_completed"]
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
            print("タスクチェックに成功しました")
            print(
                f"タスクチェック:task_id:{task.task_id}, title:{task.title}, is_completed:{task.is_completed}"
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
    if "nc_mode" not in session and "c_mode" not in session:
        session["nc_mode"] = 0
        session["c_mode"] = 0
    # 30分を期限設定しておく
    if "dl_time" not in session:
        session["dl_time"] = 15
    # session.pop("_flashes", None)


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


@app.route("/setting", methods=["GET", "POST"])
@login_required
def setting():
    if request.method == "GET":
        dl_time_mode = current_user.dl_time
        print(current_user.dl_time)
        return render_template("testtemp/setting.html", dl_time_mode=dl_time_mode)
    elif request.method == "POST":
        # dl_time => 0, 1, 2
        dl_time = int(request.form.get("dl_time"))
        print(dl_time)
        current_user.dl_time = dl_time
        session["dl_time"] = convert_dl_time(dl_time)
        db.session.commit()
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
        print(user)

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


@app.route("/api/tasks/limity", methods=["GET"])
@login_required
def get_limity_tasks():
    now = datetime.now()
    limity_tasks = Tasks.query.filter(
        Tasks.deadline < now,
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
        attachments = []
        slack_url = "https://hooks.slack.com/services/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"

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
        return True
    except Exception as e:
        print(f"Slack送信エラー発生しました")
        return False
    finally:
        session["is_first_slack"] = 0


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
    success = send_to_slack(limity_tasks)
    if success:
        print("送信完了")
        return jsonify({"success": True, "message": "Slack通知完了"})
    else:
        print("送信失敗")
        return jsonify({"success": False, "message": "Slack通知失敗"})


# @app.route("/api/slack/notify_limit", methods=["POST"])
# @login_required
# def notify_limit_tasks():
#     try:
#         data = request.get_json()
#         limity_tasks = data.get("limity_tasks", [])

#         if not limity_tasks:
#             return jsonify({"success": True, "message": "期限切れタスクはありません"})

#         # Slack通知を送信
#         success = send_to_slack(limity_tasks)

#         if success:
#             return jsonify(
#                 {
#                     "success": True,
#                     "message": f"{len(limity_tasks)}件の期限切れタスクをSlackに通知しました",
#                 }
#             )
#         else:
#             return (
#                 jsonify({"success": False, "error": "Slack通知の送信に失敗しました"}),
#                 500,
#             )

#     except Exception as e:
#         print(f"API エラー: {e}")
#         return jsonify({"success": False, "error": str(e)}), 500


# def send_to_slack(tasks):
#     try:
#         text = f"期限切れタスクが{len(tasks)}件あります"
#         attachments = []

#         # ヘッダー
#         header_attachment = {
#             "color": "#ff0000",
#             "title": "⚠️ 期限切れタスク通知",
#             "text": f"*{len(tasks)}件*のタスクが期限切れです。",
#             "mrkdwn_in": ["text"],
#         }
#         attachments.append(header_attachment)

#         # 各タスク
#         for task in tasks:
#             deadline = datetime.fromisoformat(task["deadline"].replace("Z", "+00:00"))
#             delay_hours = int((datetime.now() - deadline).total_seconds() / 3600)

#             # 重要度による色分け
#             if task["importance"] == "高":
#                 color = "#ff0000"  # 赤
#                 emoji = "🔴"
#             elif task["importance"] == "中":
#                 color = "#ffa500"  # オレンジ
#                 emoji = "🟡"
#             else:
#                 color = "#008000"  # 緑
#                 emoji = "🟢"

#             # タスクのattachment（正しい形式）
#             task_attachment = {
#                 "color": color,  # 16進数カラー
#                 "title": f"{emoji} {task['title']}",
#                 "fields": [
#                     {"title": "担当者", "value": f"@{task['username']}", "short": True},
#                     {"title": "期限", "value": task["format_deadline"], "short": True},
#                     {"title": "遅延時間", "value": f"{delay_hours}時間", "short": True},
#                     {
#                         "title": "重要度",
#                         "value": f"{emoji} {task['importance']}",
#                         "short": True,
#                     },
#                 ],
#                 "mrkdwn_in": ["text", "fields"],
#             }
#             attachments.append(task_attachment)

#         # フッター
#         footer_attachment = {
#             "color": "#808080",
#             "text": f"TaskBell | 通知時刻: {datetime.now().strftime('%Y/%m/%d %H:%M')}",
#             "mrkdwn_in": ["text"],
#         }
#         attachments.append(footer_attachment)

#         # Slack送信
#         slack.notify(
#             text=text,
#             username="TaskBell Bot",
#             icon_emoji=":bell:",
#             attachments=attachments,
#         )

#         return True  # ← これが重要！

#     except Exception as e:
#         print(f"Slack送信エラー: {e}")
#         return False  # ← これも重要！

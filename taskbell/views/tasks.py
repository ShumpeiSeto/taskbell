# coding: utf-8
import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from flask_mail import Message
from sqlalchemy import desc
import slackweb

# アプリ本体のインスタンスとモデル
from taskbell import db, mail
from taskbell.models.add_task import Tasks
from taskbell.models.login_user import User

tasks_bp = Blueprint("tasks", __name__)

# --- ヘルパー関数（内部ロジック） ---


def convert_dl_time(value):
    dl_time = None
    if value == 0:
        dl_time = 15
    if value == 1:
        dl_time = 30
    if value == 2:
        dl_time = 60
    return dl_time


def send_email_notification(limity_tasks, user):
    """期限切れタスクをメールで通知"""
    try:
        task_list = "\n".join(
            [
                f"・{t.title} (期限: {t.deadline.strftime('%Y/%m/%d %H:%M')})"
                for t in limity_tasks
            ]
        )
        body = f"こんにちは {user.username} さん、\n\n期限切れのタスクが {len(limity_tasks)} 件あります：\n\n{task_list}\n\n早めの対応をお願いします。\n\nTaskBell より"

        msg = Message(
            subject=f"【TaskBell】期限切れタスク {len(limity_tasks)} 件",
            recipients=[user.email],
            body=body,
        )
        mail.send(msg)
        print(f"メール送信成功: {user.email}")
    except Exception as e:
        print(f"メール送信エラー: {e}")


def send_to_slack2(limity_tasks, user):
    """Slackに期限切れタスクを通知（詳細版）"""
    try:
        slack = slackweb.Slack(url=user.slack_url)
        attachments = []
        for task in limity_tasks:
            color = (
                "#ff0000"
                if task.importance == 2
                else "#ffa500" if task.importance == 1 else "#008000"
            )
            emoji = (
                "🔴" if task.importance == 2 else "🟡" if task.importance == 1 else "🟢"
            )

            attachments.append(
                {
                    "title": f"{emoji}{task.title}",
                    "color": color,
                    "fields": [
                        {
                            "title": "期限",
                            "value": task.deadline.strftime("%Y/%m/%d %H:%M"),
                            "short": True,
                        },
                        {
                            "title": "重要度",
                            "value": (
                                "高"
                                if task.importance == 2
                                else "中" if task.importance == 1 else "低"
                            ),
                            "short": True,
                        },
                    ],
                }
            )
        slack.notify(
            text=f"期限切れタスクが{len(limity_tasks)}件あります",
            attachments=attachments,
        )
    except Exception as e:
        print(f"Slack送信エラー: {e}")


def slack_notify(user_id):
    """スケジューラから呼ばれる通知用関数"""
    # スケジューラ（別スレッド）から呼ばれるため app_context が必要
    with current_app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                return

            now = datetime.datetime.now()
            limity_tasks = Tasks.query.filter(
                Tasks.deadline < now,
                Tasks.is_completed == False,
                Tasks.user_id == user_id,
            ).all()

            if limity_tasks:
                if user.slack_url:
                    send_to_slack2(limity_tasks, user)
                if user.email:
                    send_email_notification(limity_tasks, user)
            return True
        except Exception as e:
            print(f"通知処理エラー: {e}")


def make_deadline(dead_date, dead_time):
    """日付と時刻文字列をdatetimeオブジェクトに変換"""
    s = f"{dead_date} {dead_time}"
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")


# --- ルート定義 (@tasks_bp.route) ---


@tasks_bp.route("/my_task")
@login_required
def my_task():
    # ソート順の取得（sessionにない場合のデフォルトも考慮）
    nc_mode = session.get("nc_v_mode", 0)
    c_mode = session.get("c_v_mode", 0)

    # クエリのベース
    query = Tasks.query.filter_by(user_id=current_user.id)

    # 未完了タスクの取得
    if nc_mode == 0:
        nc_tasks = query.filter_by(is_completed=False).order_by(Tasks.deadline).all()
    else:
        nc_tasks = (
            query.filter_by(is_completed=False)
            .order_by(desc(Tasks.importance), Tasks.deadline)
            .all()
        )

    # 完了済みタスクの取得
    if c_mode == 0:
        c_tasks = query.filter_by(is_completed=True).order_by(Tasks.deadline).all()
    else:
        c_tasks = (
            query.filter_by(is_completed=True)
            .order_by(desc(Tasks.importance), Tasks.deadline)
            .all()
        )

    return render_template("testtemp/my_task.html", nc_tasks=nc_tasks, c_tasks=c_tasks)


@tasks_bp.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        deadline = make_deadline(
            request.form.get("dead_date"), request.form.get("dead_time")
        )
        importance = int(request.form.get("importance", 0))

        new_task = Tasks(
            title=title,
            deadline=deadline,
            importance=importance,
            user_id=current_user.id,
            is_completed=False,
        )
        db.session.add(new_task)
        db.session.commit()
        flash(f"タスク「{title}」を登録しました")
        return redirect(url_for("tasks.my_task"))

    return render_template("testtemp/new_task.html")


@tasks_bp.route("/api/checked/<int:task_id>", methods=["POST"])
@login_required
def api_check_task(task_id):
    task = Tasks.query.filter_by(
        task_id=task_id, user_id=current_user.id
    ).first_or_404()
    task.is_completed = not task.is_completed
    db.session.commit()
    return jsonify({"status": "success", "is_completed": task.is_completed})


@tasks_bp.route("/setting", methods=["GET", "POST"])
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

        # スケジュールの再登録
        # global 宣言は不要（__init__.py の scheduler_thread を直接いじらないため）
        from taskbell import init_scheduler

        # 既存のスケジュールをキャンセルして再登録
        from taskbell.views.tasks import remove_user_schedule, slack_notify
        import schedule

        remove_user_schedule(current_user.id)
        schedule.every().days.at(morning_time_str).do(slack_notify, current_user.id)

        flash("設定を保存しました")
        return redirect(url_for("tasks.my_task"))


@tasks_bp.route("/slack_help")
@login_required
def slack_help():
    # 入力途中のメールアドレスが戻ると空にならないかどうか
    return render_template("testtemp/slack_help.html")


def remove_user_schedule(user_id):
    import schedule
    from taskbell.views.tasks import slack_notify

    jobs_to_remove = []
    for job in schedule.jobs:
        if (
            hasattr(job.job_func, "args")
            and len(job.job_func.args) > 0
            and job.job_func.args[0] == user_id
        ):
            jobs_to_remove.append(job)
    for job in jobs_to_remove:
        schedule.cancel_job(job)


@tasks_bp.route("/api/tasks/limity", methods=["GET"])
@login_required
def get_limity_tasks():
    now = datetime.datetime.now()
    # セッションまたはDBから設定時間を取得
    dl_time_value = session.get("dl_time", 15)

    # 期限が近い未完了タスクを取得
    limity_tasks = Tasks.query.filter(
        Tasks.deadline < now + datetime.timedelta(minutes=int(dl_time_value)),
        Tasks.is_completed == False,
        Tasks.user_id == current_user.id,
    ).all()

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


@tasks_bp.route("/api/get_mytasks", methods=["GET"])
@login_required
def get_mytasks():
    try:
        my_tasks = Tasks.query.filter(Tasks.user_id == current_user.id).all()
        tasks_data = []
        for task in my_tasks:
            tasks_data.append(
                {
                    "id": task.task_id,
                    "title": task.title,
                    "deadline": task.deadline.isoformat(),
                    "format_deadline": task.deadline.strftime("%Y/%m/%d %H:%M"),
                    "importance": task.importance,
                }
            )
        return jsonify({"success": True, "data": tasks_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@tasks_bp.route("/api/task/create", methods=["POST"])
@login_required
def create_task_api():
    data = request.get_json()
    deadline = datetime.datetime.strptime(data["deadline"], "%Y-%m-%d %H:%M")

    new_task = Tasks(
        title=data["title"],
        deadline=deadline,
        importance=data["importance"],
        user_id=current_user.id,
        is_completed=False,
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "data": {
                "task_id": new_task.task_id,
                "title": new_task.title,
                "deadline": new_task.deadline.isoformat(),
                "importance": new_task.importance,
            },
        }
    )


def check(task_id, task):
    with current_app.app_context():
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


def delete(task_id):
    with current_app.app_context():
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


# API Versionを追加してみる
@tasks_bp.route("/api/uncheck/<int:task_id>", methods=["POST"])
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


def update(task, update_info):
    with current_app.app_context():
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


@tasks_bp.route("/api/task/update/<int:task_id>", methods=["POST"])
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


@tasks_bp.route("/api/get_task/<int:task_id>", methods=["GET"])
@login_required
def api_get_task(task_id):
    with current_app.app_context():
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


@tasks_bp.route("/delete_task/<int:task_id>", methods=["GET", "POST"])
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


@tasks_bp.route("/api/delete_task/<int:task_id>", methods=["POST"])
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


@tasks_bp.route("/api/update_deadlines", methods=["POST"])
@login_required  # ★ ログイン必須も追加
def update_deadlines():
    try:
        print("=" * 50)
        print("update_deadlines ルートが呼ばれました")

        data = request.json
        print(f"受信データ: {data}")

        updates = data.get("updates", [])
        print(f"更新対象タスク数: {len(updates)}")

        for update in updates:
            task_id = update["task_id"]
            new_deadline = update["deadline"]

            print(f"タスクID {task_id} を更新中: {new_deadline}")

            # ★★★ Tasks に修正！ ★★★
            task = Tasks.query.get(task_id)
            if task:
                # ISO形式の文字列をdatetimeに変換
                task.deadline = datetime.datetime.fromisoformat(
                    new_deadline.replace("Z", "+00:00")
                )
                print(f"タスクID {task_id} の期限を更新: {task.deadline}")
            else:
                print(f"警告: タスクID {task_id} が見つかりません")

        # 全部まとめてコミット
        db.session.commit()
        print("データベース更新成功！")

        return jsonify(
            {"status": "success", "message": f"{len(updates)}件のタスクを更新しました"}
        )

    except Exception as e:
        db.session.rollback()
        print(f"エラー発生: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

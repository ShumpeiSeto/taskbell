from flask import render_template, request, redirect, Flask, flash, session
from taskbell import app, db
from .models.add_task import Tasks
from .models.login_user import User
import datetime

from sqlalchemy import desc

# from flask_sqlalchemy import desc
from flask_login import login_user, current_user, login_required, logout_user


# 手動テーブル削除と作成用（テスト時）
def init_db():
    # DB作成する(一旦削除したうえで)
    db.drop_all()
    db.create_all()


# 期限日時設定関数。秒以下の扱いでエラーあるので、%Sのないものも用意
def make_deadline(dead_date, dead_time):
    s = f"{dead_date} {dead_time}"
    s_format = "%Y-%m-%d %H:%M"
    deadline = datetime.datetime.strptime(s, s_format)
    print(deadline)
    return deadline


def make_deadline2(dead_date, dead_time):
    s = f"{dead_date} {dead_time}"
    s_format = "%Y-%m-%d %H:%M:%S"
    deadline = datetime.datetime.strptime(s, s_format)
    print(deadline)
    return deadline


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
    if "deadminutes" not in session:
        session["dead_minutes"] = 30
    # session.pop("_flashes", None)


@app.route("/my_task")
@login_required
def my_task():
    all_tasks = Tasks.query.order_by(Tasks.deadline)
    all_tasks_desc = Tasks.query.order_by(desc(Tasks.importance), Tasks.deadline)
    if session["nc_mode"] == 0:
        nc_tasks = all_tasks.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 0
        )
    elif session["nc_mode"] == 1:
        nc_tasks = all_tasks_desc.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 0
        )

    if session["c_mode"] == 0:
        c_tasks = all_tasks.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 1
        )
    elif session["c_mode"] == 1:
        c_tasks = all_tasks_desc.filter(Tasks.user_id == current_user.id).filter(
            Tasks.is_completed == 1
        )

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
        session["nc_mode"] = 1
    if flg == 2:
        session["nc_mode"] = 0
    if flg == 3:
        session["c_mode"] = 1
    if flg == 4:
        session["c_mode"] = 0
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
    logout_user()
    # session.pop("_flashes", None)
    session.clear()
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("testtemp/signup.html")
    elif request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        c_password = request.form.get("conf_password", "").strip()
        target_user = dict(username=username, password=password)

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

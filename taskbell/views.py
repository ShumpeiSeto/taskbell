from flask import render_template, request, redirect
from taskbell import app, db
from .models.add_task import Tasks
import datetime


def init_db():
    # DB作成する(一旦削除したうえで)
    db.drop_all()
    db.create_all()


def make_deadline(dead_date, dead_time):
    s = f"{dead_date} {dead_time}"
    s_format = "%Y-%m-%d %H:%M"
    deadline = datetime.datetime.strptime(s, s_format)
    print(deadline)
    return deadline


def make_deadline2(dead_date, dead_time):
    s = f"{dead_date} {dead_time}"
    s_format = "%Y-%m-%d %H:%M"
    deadline = datetime.datetime.strptime(s, s_format)
    print(deadline)
    return deadline


def insert(task_obj):
    with app.app_context():
        print("==========1件登録==========")
        task = Tasks(
            title=task_obj["title"], deadline=task_obj["deadline"], is_completed=False
        )
        db.session.add(task)
        db.session.commit()
    return redirect("/my_task")


def update(task, update_info):
    with app.app_context():
        print("==========1件更新==========")
        # target_task = Tasks.query.filter(Tasks.task_id == task.task_id).first()
        # task_id = task.task_id
        # target_task = Tasks.query.get(task_id)
        task.title = update_info["title"]
        task.deadline = update_info["dead_line"]
        task.is_completed = update_info["is_completed"]
        print(f"task-->{task}")
        print(f"update_info-->{update_info}")
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
    print("更新処理がおわりました")


# app オブジェにルートを登録する
@app.route("/")
def index():
    return "Hello World"
    # return render_template("testtemp/index.html", title="Index Page")


@app.route("/my_task")
def my_task():
    alltasks = Tasks.query.all()
    print(alltasks)
    return render_template(
        "testtemp/my_task.html", alltasks=alltasks, enumerate=enumerate
    )


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "GET":
        return render_template("testtemp/new_task.html")
    elif request.method == "POST":
        title = request.form.get("title")
        dead_date = request.form.get("dead_date")
        dead_time = request.form.get("dead_time")
        deadline = make_deadline(dead_date, dead_time)
        is_completed = False
        target_task = dict(title=title, deadline=deadline, is_completed=is_completed)
        print(target_task)
        insert(target_task)
    return render_template("testtemp/new_task.html")


@app.route("/edit_task/<int:index>", methods=["GET", "POST"])
def edit_task(index):
    task = Tasks.query.filter(Tasks.task_id == index + 1).first()
    print(task)
    if request.method == "GET":
        return render_template("testtemp/edit_task.html", task=task)
    elif request.method == "POST":
        print("更新がはじまります。")
        title = request.form.get("title")
        dead_date = request.form.get("dead_date")
        dead_time = request.form.get("dead_time")
        dead_line = make_deadline2(dead_date, dead_time)
        is_completed = False
        update_info = {
            "title": title,
            "dead_line": dead_line,
            "is_completed": is_completed,
        }
        update(task, update_info)
    # print(index, task)
    # return render_template("testtemp/edit_task.html", task=task)
    # return redirect("/my_task")
    # return render_template("testtemp/edit_task.html", task=task)
    return redirect("/my_task")


# アクセスするとテーブル削除と作成
@app.route("/make_table")
def make_table():
    with app.app_context():
        init_db()
    return redirect("/add_task")

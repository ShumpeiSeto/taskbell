from flask import render_template, request, redirect
from taskbell import app, db
from .models.add_task import Tasks
import datetime


def init_db():
    # DB作成する(一旦削除したうえで)
    db.drop_all()
    db.create_all()


def insert(task_obj):
    with app.app_context():
        print("==========1件登録==========")
        task = Tasks(
            title=task_obj["name"], deadline=task_obj["deadline"], is_completed=False
        )
        db.session.add(task)
        db.session.commit()


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
        name = request.form.get("title")
        dead_date = request.form.get("dead_date")
        dead_time = request.form.get("dead_time")
        s = f"{dead_date} {dead_time}"
        s_format = "%Y-%m-%d %H:%M"
        deadline = datetime.datetime.strptime(s, s_format)
        is_completed = False
        # target_task = {"name": name, "deadline": deadline, "is_completed": is_completed}
        target_task = dict(name=name, deadline=deadline, is_completed=is_completed)
        print(target_task)
        insert(target_task)
    return render_template("testtemp/new_task.html")


# アクセスするとテーブル削除と作成
@app.route("/make_table")
def make_table():
    with app.app_context():
        init_db()
    return redirect("/add_task")

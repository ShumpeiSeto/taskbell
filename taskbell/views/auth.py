# # auth.py の中身
# from flask import Blueprint, render_template, request, redirect, session, flash
# from taskbell import db
# from taskbell.models.login_user import User  # 必要なモデルをインポート
# from werkzeug.security import generate_password_hash
# from flask_login import login_user, logout_user

# # 1. Blueprintの定義
# auth = Blueprint("auth", __name__)


# # 2. @app.route ではなく @auth.route
# @auth.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "GET":
#         return render_template("testtemp/login.html")
#     elif request.method == "POST":
#         # if current_user.is_authenticated:
#         #     return render_template("testtemp/index.html", current_user=current_user)

#         # ユーザーが存在するかユーザ名で検索する
#         username = request.form.get("username", "").strip()
#         user = User.query.filter(User.username == username).one_or_none()
#         password = request.form.get("password", "").strip()
#         session["nc_v_mode"] = user.nc_v_mode
#         session["c_v_mode"] = user.c_v_mode
#         session["dl_time"] = user.dl_time
#         session["is_first_slack"] = 1
#         # print(user)

#         # instanceつくる
#         # overrrideしていたが継承元UserMixinのものでOKだった
#         if (user is not None) and (user.is_authenticated(username, password)):
#             # if user.is_authenticated:
#             login_user(user)
#             flash("認証成しました\n")
#             flash(f"あなたは{user.username}です\n")
#             return redirect("/my_task")
#         else:
#             flash("ユーザー名とパスワードが一致していません")
#             flash("もう一度入力してください")
#             return redirect("/login")
#     return render_template("testtemp/login.html")
#     # views.py にあった login の中身をここに移動
#     ...

# 下記テスト（整理）
# coding: utf-8
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash

# アプリ本体のインスタンスとモデルをインポート
from taskbell import db
from taskbell.models.login_user import User

# Blueprintの定義
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")  # ここを登録
def index():
    logout_user()
    session.clear()
    return render_template("testtemp/index.html")


# --- 会員登録 ---
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("testtemp/signup.html")

    elif request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # バリデーション
        if not username or not password:
            flash("ユーザー名とパスワードを入力してください")
            return redirect(url_for("auth.signup"))

        # 既存ユーザーの確認
        user = User.query.filter_by(username=username).first()
        if user:
            flash("このユーザー名は既に使用されています")
            return redirect(url_for("auth.signup"))

        # 新規ユーザー作成
        new_user = User(
            username=username,
            password=generate_password_hash(password, method="pbkdf2:sha256"),
        )
        db.session.add(new_user)
        db.session.commit()

        flash("会員登録が完了しました。ログインしてください。")
        return redirect(url_for("auth.login"))


# --- ログイン ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # すでにログイン済みならメイン画面へ
        if current_user.is_authenticated:
            return redirect(url_for("tasks.my_task"))
        return render_template("testtemp/login.html")

    elif request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter(User.username == username).one_or_none()

        if user and user.is_authenticated(username, password):
            login_user(user)

            # セッション変数のセット（既存のviews.pyから継承）
            session["nc_v_mode"] = user.nc_v_mode
            session["c_v_mode"] = user.c_v_mode
            session["dl_time"] = user.dl_time
            session["is_first_slack"] = 1

            flash("ログインしました")
            # タスク一覧画面（tasks Blueprint）へリダイレクト
            return redirect(url_for("tasks.my_task"))
        else:
            flash("ユーザー名またはパスワードが正しくありません")
            return redirect(url_for("auth.login"))


# --- ログアウト ---
@auth_bp.route("/logout")
def logout():
    # 変更をコミットしてセッションをクリア
    db.session.commit()
    session.clear()
    logout_user()
    flash("ログアウトしました")
    return redirect(url_for("auth.login"))

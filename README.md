

---------セットアップ方法---------

1. リポジトリのクローン

git clone ShumpeiSeto/flask2
cd flask2


下記はflask2フォルダ内にて

2. 仮想環境の作成と有効化

(Windowsの場合)
python -m venv venv
venv\Scripts\activate


3. 依存関係のインストール
pip install -r requirements.txt

4. データベースの初期化（）
※相談できておりませんでした。
※外部キー設定（テーブル連携）で何度もユーザー＆タスク登録しなおす手間があり、migrationに挑戦しました。
※下記でうまく動かない場合はpython server.pyで起動後に、/make_tableにアクセスすると、テーブル削除＆作成できるのでしてください。

# マイグレーションファイルが既にある場合
flask db upgrade

# 初回セットアップの場合（必要に応じて）
flask db init
flask db migrate -m "Initial migration"
flask db upgrade


5. アプリケーションの起動
flask2フォルダ内にて、

python server.py



【起動に関して】
gitの除外設定が甘くデータベースファイルなどが引き続き追跡されているので、なにかあれば/make_tableにアクセスして、
テーブル削除＆作成してください。



------------中身の構成------------


主にflask2内のtaskbellフォルダ内に内容があります。まぎらわしい感じになっています。
flaskで主に起動させるファイルはapp.pyと名前をつけるのが慣例だったようですが、
私の場合はviews.pyとなっています。

flask2/
├── .vscode/              # VSCode設定
│   └── launch.json
├── instance/             
│   └── sample_tasks.db   # SQLiteデータベース
├── migrations/           # マイグレーションファイル
├── taskbell/            # メインアプリケーション
│   ├── __pycache__/
│   ├── models/          # データモデル
│   │   ├── __pycache__/
│   │   ├── add_task.py  # タスクモデル
│   │   └── login_user.py # ユーザーモデル
│   ├── static/          # 静的ファイル（CSSなど）
│   ├── templates/       # HTMLテンプレート
│   ├── __init__.py      # はじめに動くもの
│   ├── config.py        # 設定ファイル
│   └── views.py         # ビュー関数(Routingなどここに多く記述）
├── venv/                # 仮想環境
├── .gitignore           # Git除外設定
├── .sqliterc            # SQLite設定
├── requirements.txt     # Python依存関係
└── server.py           # アプリケーション起動ファイル

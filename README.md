# Flask2 セットアップガイド

## セットアップ方法

### 1. リポジトリのクローン
```bash
git clone ShumpeiSeto/flask2
cd flask2
```
> **注意**: 以下の操作は全てflask2フォルダ内で実行してください

### 2. 仮想環境の作成と有効化
**Windowsの場合:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. データベースの初期化

> **⚠️ 重要な注意事項**
> - マイグレーション機能はまだ調整中です
> - 外部キー設定（テーブル連携）の関係で、何度もユーザー＆タスクを登録し直す手間が発生する可能性があります
> - 下記の方法でうまく動かない場合は、`python server.py`で起動後に `/make_table` にアクセスすると、テーブル削除＆作成ができます

#### マイグレーションファイルが既にある場合
```bash
flask db upgrade
```

#### 初回セットアップの場合
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. アプリケーションの起動
flask2フォルダ内で以下を実行:
```bash
python server.py
```

## 起動に関しての注意点

> **Git除外設定について**  
> gitの除外設定が不完全で、データベースファイルなどが追跡されている状態です。  
> 何か問題が発生した場合は、`/make_table` にアクセスしてテーブルの削除＆作成を行ってください。

## プロジェクト構成

主な機能は `flask2/taskbell/` フォルダ内に実装されています。

> **命名について**  
> Flaskでは通常、メインファイルを `app.py` と命名するのが慣例ですが、このプロジェクトでは `views.py` としています。

```
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
│   ├── __init__.py      # 初期化ファイル
│   ├── config.py        # 設定ファイル
│   └── views.py         # ビュー関数（ルーティングなど）
├── venv/                # 仮想環境
├── .gitignore           # Git除外設定
├── .sqliterc            # SQLite設定
├── requirements.txt     # Python依存関係
└── server.py           # アプリケーション起動ファイル
```

## トラブルシューティング

### データベースの問題が発生した場合
1. アプリケーションを起動: `python server.py`
2. ブラウザで `/make_table` にアクセス
3. テーブルの削除＆再作成が実行されます

### マイグレーションがうまくいかない場合
```bash
# マイグレーション環境をリセット
rm -rf migrations/
rm instance/sample_tasks.db

# 再初期化
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

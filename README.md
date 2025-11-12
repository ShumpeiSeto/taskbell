# TaskBell - 期限通知 ToDo アプリ

`TaskBell` は、日々のタスク管理をサポートし、期限が近づくと通知してくれる Web アプリケーションです。Flask をベースに構築されています。

## ✨ 主な機能

- **ユーザー認証:** 新規登録とログイン機能
- **タスク管理 (CRUD):** タスクの追加、編集、削除、完了/未完了の切り替え
- **タスク詳細設定:** タスクには「期限（日付・時間）」と「重要度（★, ★★, ★★★）」を設定可能
- **ソート機能:** 未完了・完了済みタスクをそれぞれ「日付順」「重要度順」で並び替え可能
- **期限前通知 (アプリ内):** ユーザーが設定した時間（15 分/30 分/60 分前）になると、アプリ上で通知モーダルが表示
- **期限切れ通知 (スケジュール実行):** 1 日 1 回、設定した時刻に期限切れタスクを検知し、**Email** または **Slack** へ自動で通知

## 📸 スクリーンショット

## 🚀 セットアップ方法

### 1. リポジトリのクローン

```bash
git clone https://github.com/ShumpeiSeto/taskbell
cd taskbell
```

> **注意:** 以下の操作は全て `taskbell` フォルダ内で実行してください

### 2. 仮想環境の作成と有効化

**Windows の場合:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux の場合:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. データベースの初期化

> ⚠️ **重要な注意事項**
>
> マイグレーション機能はまだ調整中です。
>
> 下記の方法でうまく動かない場合は、`python server.py` で起動後に `/make_table` にアクセスすると、テーブル削除＆作成ができます。

**マイグレーションファイルが既にある場合:**

```bash
flask db upgrade
```

**初回セットアップの場合:**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. アプリケーションの起動

`taskbell` フォルダ内で以下を実行:

```bash
python server.py
```

（`FLASK_ENV=development` が `.flaskenv` で設定されているため、デバッグモードで起動します）

## 🔧 プロジェクト構成

主な機能は `taskbell/taskbell/` フォルダ内に実装されています。

```
taskbell/
├── .vscode/              # VSCode設定
├── migrations/           # マイグレーションファイル
├── taskbell/             # メインアプリケーション
│   ├── models/           # データモデル (Task, User)
│   ├── static/           # 静的ファイル (CSS, JS, 画像)
│   ├── templates/        # HTMLテンプレート
│   ├── __init__.py       # Flaskアプリ初期化, スケジューラ起動
│   ├── config.py         # 設定ファイル (DBの場所など)
│   └── views.py          # ビュー関数 (ルーティング, API)
├── venv/                 # 仮想環境
├── .flaskenv             # Flask環境変数
├── .gitignore            # Git除外設定
├── requirements.txt      # Python依存関係
├── server.py             # アプリケーション起動ファイル
└── sample_tasks.db       # SQLiteデータベース (config.pyで定義)
```

## 💡 トラブルシューティング

### データベースの問題が発生した場合

1. アプリケーションを起動: `python server.py`
2. ブラウザで `/make_table` にアクセス
3. テーブルの削除＆再作成が実行されます

### マイグレーションがうまくいかない場合

```bash
# マイグレーション環境をリセット
rm -rf migrations/
rm sample_tasks.db  # (Windowsの場合は del sample_tasks.db)

# 再初期化
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 📝 ライセンス

MIT License

## 👤 作者

Shumpei Seto

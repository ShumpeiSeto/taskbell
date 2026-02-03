# DEBUG = True
# # Database の置き場所
# SQLALCHEMY_DATABASE_URI = "sqlite:///sample_tasks.db"
# # 変更できるかどうか
# SQLALCHEMY_TRACK_MODIFICATIONS = True

import os

DEBUG = True

# PostgreSQLへの接続設定
# 形式: postgresql://[ユーザー名]:[パスワード]@[ホスト名]:[ポート番号]/[データベース名]
SQLALCHEMY_DATABASE_URI = (
    os.environ.get("DATABASE_URL")
    or "postgresql://postgres:psms855iach!@localhost:5432/taskbell"
)

SQLALCHEMY_TRACK_MODIFICATIONS = True

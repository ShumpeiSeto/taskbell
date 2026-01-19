# coding: utf-8
from flask import current_app
from taskbell import db
from taskbell.models.add_task import Tasks


def get_task_by_id(task_id, user_id):
    """特定のユーザーのタスクを取得"""
    return Tasks.query.filter_by(task_id=task_id, user_id=user_id).first()


def create_task(title, deadline, importance, user_id):
    """新規タスク作成"""
    new_task = Tasks(
        title=title,
        deadline=deadline,
        importance=importance,
        user_id=user_id,
        is_completed=False,
    )
    db.session.add(new_task)
    db.session.commit()
    return new_task


def update_task_logic(task, update_info):
    """タスク情報の更新"""
    with current_app.app_context():
        task.title = update_info["title"]
        task.deadline = update_info["dead_line"]
        task.importance = update_info["importance"]
        try:
            db.session.merge(task)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"更新エラー: {e}")
            return False


def delete_task_logic(task_id):
    """タスク削除"""
    with current_app.app_context():
        task = Tasks.query.get(task_id)
        if task:
            try:
                db.session.delete(task)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"削除エラー: {e}")
                return False
        return False


def toggle_task_status(task):
    """完了/未完了の切り替え"""
    with current_app.app_context():
        task.is_completed = not task.is_completed
        try:
            db.session.merge(task)
            db.session.commit()
            return task.is_completed
        except Exception as e:
            db.session.rollback()
            print(f"ステータス更新エラー: {e}")
            return None

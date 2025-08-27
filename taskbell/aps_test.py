# slack定期実行のた目のテスト用
from apscheduler.schedulers.background import BackgroundScheduler

def post_to_slack():
    print('定期実行なう！')


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(post_to_slack, 'interval', seconds=30)
    scheduler.start()
    print('定期実行が開始しました')
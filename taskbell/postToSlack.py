import slackweb
# slack定期実行のた目のテスト用
from apscheduler.schedulers.background import BackgroundScheduler

def post_to_slack():
    slack = slackweb.Slack(
        url="https://hooks.slack.com/services/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"
    )

    attachment = {
        "author_name": "peipei",
        "title": "期限が近付いているタスクがあります",
        "text": "期限が近付いているタスクは下記です",
        "pretext": "Optional text that appears above",
        "color": "#36a64f",
    }
    slack.notify(text='遅延タスクあり', attachments=[attachment])


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(post_to_slack, 'interval', seconds=300)
    scheduler.start()
    print('定期実行が開始しました')
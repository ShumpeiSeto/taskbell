import slackweb

# from flask_login import current_user


def post_to_slack(post_text):
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
    slack.notify(text=post_text, attachments=[attachment])


# post_to_slack('期限切れタスクあり')

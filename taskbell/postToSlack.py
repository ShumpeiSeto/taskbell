import slackweb

def post_to_slack(post_text):
    slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
    slack.notify(text=post_text)
import slackweb

from pywell.entry_points import run_from_cli


DESCRIPTION = 'Send notification to Slack.'

ARG_DEFINITIONS = {
    'SLACK_WEBHOOK': 'Web hook URL for Slack.',
    'SLACK_CHANNEL': 'Slack channel to send to.',
    'SLACK_MESSAGE_TEXT': 'Text to send.'
}

REQUIRED_ARGS = [
    'SLACK_WEBHOOK', 'SLACK_CHANNEL', 'SLACK_MESSAGE_TEXT'
]


def notify_slack(args):
    slack = slackweb.Slack(url=args.SLACK_WEBHOOK)
    return slack.notify(text=args.SLACK_MESSAGE_TEXT, channel=args.SLACK_CHANNEL)


if __name__ == '__main__':
    run_from_cli(notify_slack, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)

import os

import boto3
from botocore.exceptions import ClientError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from wf_data_monitor.log import logger


class Notifier:
    def __init__(self):
        self.slack_client = None
        self.sns_client = None
        self.sns_topic_name = os.getenv("AWS_SNS_TOPIC", "clusterhealth")
        self.sns_topic_arn = None

        self._init_slack()
        self._init_sns()

    def _init_slack(self):
        slack_token = os.getenv("SLACK_BOT_TOKEN", None)
        if slack_token is not None:
            self.slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    def _init_sns(self):
        self.sns_client = boto3.client("sns")
        try:

            topics = self.sns_client.list_topics()
            topic_arn = next(
                filter(
                    lambda arn: arn.split(":")[-1] == self.sns_topic_name,
                    map(lambda topic: topic["TopicArn"], topics["Topics"]),
                )
            )

            self.sns_topic_arn = topic_arn
        except ClientError:
            logger.exception("Couldn't fetch SNS topic ARNs.")
            raise

    def send_message(self, subject, message):
        DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

        if self.sns_topic_arn and not DEBUG:
            self.sns_client.publish(TopicArn=self.sns_topic_arn, Subject=subject, Message=message)


notifier: Notifier = Notifier()

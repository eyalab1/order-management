# oms-subscribe Lambda
# POST /subscriptions
# Body: { "email": "user@example.com" }
# Subscribes the email to SNS topic oms-order-deleted.
# SNS will send a confirmation email — user must click it before receiving notifications.

import json
import boto3
import os

sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    pass  # TODO: implement

# oms-unsubscribe Lambda
# DELETE /subscriptions
# Body: { "email": "user@example.com" }
# Unsubscribes the email from SNS topic oms-order-deleted.

import json
import boto3
import os

sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    pass  # TODO: implement

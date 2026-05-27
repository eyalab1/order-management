# oms-stream-processor Lambda
# Triggered by DynamoDB Streams on REMOVE events.
# Reads OldImage (deleted order), then:
#   1. Publishes to SNS topic -> emails subscribers
#   2. Writes .txt backup file to S3

import json
import boto3
import os

sns = boto3.client('sns')
s3 = boto3.client('s3')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
S3_BUCKET = os.environ.get('S3_BUCKET')

def lambda_handler(event, context):
    pass  # TODO: implement

# oms-delete-order Lambda
# DELETE /orders/{orderId}
# Deletes the order from DynamoDB and returns immediately.
# Async side-effects (email + S3 backup) are handled by oms-stream-processor
# via DynamoDB Streams — this Lambda does NOT wait for them.

import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'orders')

def lambda_handler(event, context):
    pass  # TODO: implement

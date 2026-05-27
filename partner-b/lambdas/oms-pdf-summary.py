# oms-pdf-summary Lambda
# GET /reports/deleted-orders
# Reads all .txt backup files from S3, builds a PDF summary,
# uploads it to S3, and returns the download URL in the response body.

import json
import boto3
import os

s3 = boto3.client('s3')
S3_BUCKET = os.environ.get('S3_BUCKET')

def lambda_handler(event, context):
    pass  # TODO: implement

import json
import boto3
import os
from datetime import datetime, timezone

sns = boto3.client('sns')
s3 = boto3.client('s3')

SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
S3_BUCKET = os.environ.get('S3_BUCKET')


def lambda_handler(event, context):
    for record in event['Records']:

        # Only process deleted orders
        if record['eventName'] != 'REMOVE':
            continue

        # Extract the deleted order from the stream record
        order = extract_order(record['dynamodb']['OldImage'])

        # Send email notification to all SNS subscribers
        publish_notification(order)

        # Save .txt backup to S3
        save_backup(order)


def extract_order(old_image):
    # DynamoDB stream format wraps values: {"S": "value"} or {"N": "123"}
    # We unwrap them into a plain Python dict
    return {
        'orderId':      old_image['orderId']['S'],
        'description':  old_image['description']['S'],
        'price':        old_image['price']['N'],
        'creationDate': old_image['creationDate']['S'],
        'lastModified': old_image['lastModified']['S']
    }


def publish_notification(order):
    message = (
        f"An order has been deleted from the Order Management System.\n\n"
        f"Order Details:\n"
        f"  Order ID:     {order['orderId']}\n"
        f"  Description:  {order['description']}\n"
        f"  Price:        ${order['price']}\n"
        f"  Created:      {order['creationDate']}\n"
        f"  Last Modified:{order['lastModified']}\n"
    )

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='Order Deleted Notification',
        Message=message
    )


def save_backup(order):
    content = (
        f"Order ID:      {order['orderId']}\n"
        f"Description:   {order['description']}\n"
        f"Price:         ${order['price']}\n"
        f"Created:       {order['creationDate']}\n"
        f"Last Modified: {order['lastModified']}\n"
        f"Deleted At:    {datetime.now(timezone.utc).isoformat()}\n"
    )

    file_key = f"deleted-orders/{order['orderId']}.txt"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=file_key,
        Body=content.encode('utf-8'),
        ContentType='text/plain'
    )

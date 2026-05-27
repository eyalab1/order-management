import json
import boto3
import os

sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'DELETE,OPTIONS'
}

def lambda_handler(event, context):
    body = json.loads(event['body'])
    email = body.get('email')

    if not email:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'email is required'})
        }

    # Find the subscription ARN for this email
    subscription_arn = find_subscription_arn(email)

    if not subscription_arn:
        return {
            'statusCode': 404,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'{email} is not subscribed'})
        }

    sns.unsubscribe(SubscriptionArn=subscription_arn)

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'message': f'{email} has been unsubscribed successfully'})
    }


def find_subscription_arn(email):
    paginator = sns.get_paginator('list_subscriptions_by_topic')

    for page in paginator.paginate(TopicArn=SNS_TOPIC_ARN):
        for sub in page['Subscriptions']:
            if sub['Endpoint'] == email and sub['SubscriptionArn'] != 'PendingConfirmation':
                return sub['SubscriptionArn']

    return None

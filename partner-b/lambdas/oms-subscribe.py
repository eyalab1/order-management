import json
import boto3
import os

sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
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

    sns.subscribe(
        TopicArn=SNS_TOPIC_ARN,
        Protocol='email',
        Endpoint=email
    )

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'message': f'Confirmation email sent to {email}. Please click the link to activate notifications.'
        })
    }

import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
translate = boto3.client('translate')

TABLE_NAME = os.environ.get('TABLE_NAME', 'orders')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
}

SUPPORTED_LANGUAGES = ['es', 'fr', 'de', 'ar', 'he', 'zh']


def lambda_handler(event, context):
    # Get orderId from the URL
    order_id = event['pathParameters']['orderId']

    # Get target language from the request body
    body = json.loads(event['body'])
    target_language = body.get('targetLanguage')

    # Validate target language
    if not target_language:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'targetLanguage is required'})
        }

    if target_language not in SUPPORTED_LANGUAGES:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': f'Unsupported language. Choose from: {", ".join(SUPPORTED_LANGUAGES)}'
            })
        }

    # Get the order from DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    result = table.get_item(Key={'orderId': order_id})

    if 'Item' not in result:
        return {
            'statusCode': 404,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'Order {order_id} not found'})
        }

    order = result['Item']
    original_description = order['description']

    # Translate the description
    # SourceLanguageCode='auto' lets AWS detect the input language automatically
    translation = translate.translate_text(
        Text=original_description,
        SourceLanguageCode='auto',
        TargetLanguageCode=target_language
    )

    translated_description = translation['TranslatedText']

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'orderId': order_id,
            'originalDescription': original_description,
            'translatedDescription': translated_description,
            'targetLanguage': target_language
        })
    }

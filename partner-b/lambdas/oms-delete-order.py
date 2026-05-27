import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'orders')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'DELETE,OPTIONS'
}

def lambda_handler(event, context):
    order_id = event['pathParameters']['orderId']

    table = dynamodb.Table(TABLE_NAME)

    result = table.get_item(Key={'orderId': order_id})
    if 'Item' not in result:
        return {
            'statusCode': 404,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': f'Order {order_id} not found'})
        }

    table.delete_item(Key={'orderId': order_id})

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'message': f'Order {order_id} deleted successfully'})
    }

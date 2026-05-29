import json
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


def lambda_handler(event, context):
    # With proxy integration, the {orderId} segment of the URL arrives here.
    path_params = event.get("pathParameters") or {}
    order_id = path_params.get("orderId")
    if not order_id:
        return _response(400, {"error": "orderId is required in the path"})

    # get_item is a direct lookup by primary key: one fast, cheap read.
    # (Contrast with Get-all, which scans the whole table.)
    result = table.get_item(Key={"orderId": order_id})
    item = result.get("Item")
    if not item:
        return _response(404, {"error": f"Order {order_id} not found"})

    return _response(200, item)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
        },
        "body": json.dumps(body, default=_decimal_default),
    }


def _decimal_default(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError

import json
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


def lambda_handler(event, context):
    # Read every order from the table.
    result = table.scan()
    items = result.get("Items", [])

    # A scan returns at most 1MB per call, so page through any remainder.
    while "LastEvaluatedKey" in result:
        result = table.scan(ExclusiveStartKey=result["LastEvaluatedKey"])
        items.extend(result.get("Items", []))

    # Sort by creation date, newest first. Flip reverse=False for oldest first.
    items.sort(key=lambda o: o.get("creationDate", ""), reverse=True)

    return _response(200, items)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
        },
        # default= handles DynamoDB Decimal values, which json cannot serialize on its own.
        "body": json.dumps(body, default=_decimal_default),
    }


def _decimal_default(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError

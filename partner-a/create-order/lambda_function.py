import json
import uuid
from decimal import Decimal
from datetime import datetime, timezone

import boto3

# boto3 is preinstalled in the Lambda Python runtime, so there is nothing to package.
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


def lambda_handler(event, context):
    # API Gateway delivers the request body as a JSON STRING in event["body"].
    try:
        body = json.loads(event.get("body") or "{}")
    except (json.JSONDecodeError, TypeError):
        return _response(400, {"error": "Request body must be valid JSON"})

    price = body.get("price")
    description = body.get("description")
    if price is None or description is None:
        return _response(400, {"error": "price and description are required"})

    now = datetime.now(timezone.utc).isoformat()
    order_id = str(uuid.uuid4())

    # DynamoDB stores numbers as Decimal, not float, so convert before saving.
    item = {
        "orderId": order_id,
        "price": Decimal(str(price)),
        "description": description,
        "creationDate": now,
        "lastModified": now,
    }
    table.put_item(Item=item)

    # Return the saved order. Use the original price value for clean JSON output.
    return _response(201, {
        "orderId": order_id,
        "price": price,
        "description": description,
        "creationDate": now,
        "lastModified": now,
    })


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
        },
        "body": json.dumps(body),
    }

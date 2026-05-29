import json
from decimal import Decimal
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    order_id = path_params.get("orderId")
    if not order_id:
        return _response(400, {"error": "orderId is required in the path"})

    try:
        body = json.loads(event.get("body") or "{}")
    except (json.JSONDecodeError, TypeError):
        return _response(400, {"error": "Request body must be valid JSON"})

    price = body.get("price")
    description = body.get("description")
    if price is None and description is None:
        return _response(400, {"error": "Provide price and/or description to update"})

    # Build the update so only the provided fields change. lastModified always updates.
    # #names are placeholders that avoid clashing with DynamoDB reserved words.
    now = datetime.now(timezone.utc).isoformat()
    set_parts = ["#lm = :m"]
    names = {"#lm": "lastModified"}
    values = {":m": now}
    if price is not None:
        set_parts.append("#p = :p")
        names["#p"] = "price"
        values[":p"] = Decimal(str(price))
    if description is not None:
        set_parts.append("#d = :d")
        names["#d"] = "description"
        values[":d"] = description

    try:
        result = table.update_item(
            Key={"orderId": order_id},
            UpdateExpression="SET " + ", ".join(set_parts),
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            # Only update if the order already exists; otherwise update_item would
            # silently create a new one (upsert). This makes "not found" a real 404.
            ConditionExpression="attribute_exists(orderId)",
            ReturnValues="ALL_NEW",  # return the item as it looks after the update
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return _response(404, {"error": f"Order {order_id} not found"})
        raise

    return _response(200, result["Attributes"])


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

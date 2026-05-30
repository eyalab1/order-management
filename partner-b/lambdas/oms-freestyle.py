import json
import boto3
from datetime import datetime, timedelta, timezone

# Freestyle: Amazon CloudWatch.
# Reads the Invocations metric AWS auto-emits for each Lambda over the last 24h
# and returns aggregate system stats (orders created, deleted, listed, updated).
cloudwatch = boto3.client("cloudwatch")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
}


def invocations_of(function_name, start, end):
    r = cloudwatch.get_metric_statistics(
        Namespace="AWS/Lambda",
        MetricName="Invocations",
        Dimensions=[{"Name": "FunctionName", "Value": function_name}],
        StartTime=start,
        EndTime=end,
        Period=86400,
        Statistics=["Sum"],
    )
    points = r.get("Datapoints", [])
    return int(points[0]["Sum"]) if points else 0


def lambda_handler(event, context):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=1)

    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps({
            "windowHours": 24,
            "metrics": {
                "ordersCreated": invocations_of("oms-create-order", start, end),
                "ordersDeleted": invocations_of("oms-delete-order", start, end),
                "ordersListed":  invocations_of("oms-get-all-orders", start, end),
                "ordersUpdated": invocations_of("oms-update-order", start, end),
            },
        }),
    }

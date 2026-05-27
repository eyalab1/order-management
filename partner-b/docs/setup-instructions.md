# Partner B Setup Instructions for Eyal (Integration Account)

## Resources to create in AWS Console

### 1. SNS Topic
- Name: `oms-order-deleted`
- Type: Standard

### 2. S3 Bucket
- Name: `oms-backups-<your-accountId>`
- Region: same as all other resources
- Block public access: ON (PDFs served via pre-signed URLs)

### 3. Lambda Functions (paste code from partner-b/lambdas/)

| Lambda name | File | Trigger | Environment variables |
|---|---|---|---|
| `oms-delete-order` | oms-delete-order.py | API Gateway DELETE /orders/{orderId} | TABLE_NAME=orders |
| `oms-stream-processor` | oms-stream-processor.py | DynamoDB Streams on `orders` table (REMOVE) | SNS_TOPIC_ARN, S3_BUCKET |
| `oms-subscribe` | oms-subscribe.py | API Gateway POST /subscriptions | SNS_TOPIC_ARN |
| `oms-unsubscribe` | oms-unsubscribe.py | API Gateway DELETE /subscriptions | SNS_TOPIC_ARN |
| `oms-pdf-summary` | oms-pdf-summary.py | API Gateway GET /reports/deleted-orders | S3_BUCKET |
| `oms-freestyle` | oms-freestyle.py | API Gateway (TBD) | TBD |

### 4. IAM permissions per Lambda

**oms-delete-order**: `dynamodb:DeleteItem` on table `orders`

**oms-stream-processor**: `sns:Publish` on topic `oms-order-deleted`, `s3:PutObject` on bucket `oms-backups-*`, `dynamodb:GetRecords` + `dynamodb:GetShardIterator` + `dynamodb:DescribeStream` + `dynamodb:ListStreams`

**oms-subscribe**: `sns:Subscribe` on topic `oms-order-deleted`

**oms-unsubscribe**: `sns:Unsubscribe`, `sns:ListSubscriptionsByTopic` on topic `oms-order-deleted`

**oms-pdf-summary**: `s3:GetObject` + `s3:PutObject` + `s3:ListBucket` on bucket `oms-backups-*`

**oms-freestyle**: TBD (depends on service chosen)

### 5. DynamoDB Streams
- Enable Streams on the `orders` table: View type = **New and old images**
- Set `oms-stream-processor` as the trigger

### 6. CORS (important — do this when creating routes)
Enable CORS on all Partner B routes in API Gateway:
- DELETE /orders/{orderId}
- POST /subscriptions
- DELETE /subscriptions
- GET /reports/deleted-orders

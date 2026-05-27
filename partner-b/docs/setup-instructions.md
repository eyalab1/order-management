# Partner B Setup Instructions for Eyal (Integration Account)

## Resources to create in AWS Console

### 1. SNS Topic
- Name: `oms-order-deleted`
- Type: Standard

### 2. S3 Bucket
- Name: `oms-backups-<your-accountId>`
- Region: same as all other resources
- Block public access: ON (PDFs served via pre-signed URLs)

### 3. Lambda Layer for PDF generation (do this once)
Run these commands on your machine, then upload the zip as a Lambda Layer:
```bash
mkdir -p layer/python
pip install reportlab -t layer/python
cd layer && zip -r reportlab-layer.zip python/
```
In AWS Console:
- Lambda → Layers → Create Layer
- Name: `reportlab`
- Upload `reportlab-layer.zip`
- Runtime: Python 3.12
- Attach this layer to `oms-pdf-summary` Lambda only

### 4. Lambda Functions (paste code from partner-b/lambdas/)

| Lambda name | File | Trigger | Environment variables |
|---|---|---|---|
| `oms-delete-order` | oms-delete-order.py | API Gateway DELETE /orders/{orderId} | TABLE_NAME=orders |
| `oms-stream-processor` | oms-stream-processor.py | DynamoDB Streams on `orders` table (REMOVE) | SNS_TOPIC_ARN, S3_BUCKET |
| `oms-subscribe` | oms-subscribe.py | API Gateway POST /subscriptions | SNS_TOPIC_ARN |
| `oms-unsubscribe` | oms-unsubscribe.py | API Gateway DELETE /subscriptions | SNS_TOPIC_ARN |
| `oms-pdf-summary` | oms-pdf-summary.py | API Gateway GET /reports/deleted-orders | S3_BUCKET |
| `oms-freestyle` | oms-freestyle.py | API Gateway POST /orders/{orderId}/translate | TABLE_NAME=orders |

### 5. IAM permissions per Lambda

**oms-delete-order**
- `dynamodb:GetItem` on table `orders`
- `dynamodb:DeleteItem` on table `orders`

**oms-stream-processor**
- `sns:Publish` on topic `oms-order-deleted`
- `s3:PutObject` on bucket `oms-backups-*`
- `dynamodb:GetRecords`
- `dynamodb:GetShardIterator`
- `dynamodb:DescribeStream`
- `dynamodb:ListStreams`

**oms-subscribe**
- `sns:Subscribe` on topic `oms-order-deleted`

**oms-unsubscribe**
- `sns:ListSubscriptionsByTopic` on topic `oms-order-deleted`
- `sns:Unsubscribe`

**oms-pdf-summary**
- `s3:ListBucket` on bucket `oms-backups-*`
- `s3:GetObject` on bucket `oms-backups-*`
- `s3:PutObject` on bucket `oms-backups-*`

**oms-freestyle**
- `dynamodb:GetItem` on table `orders`
- `translate:TranslateText`

### 6. DynamoDB Streams
- Enable Streams on the `orders` table: View type = **New and old images**
- Set `oms-stream-processor` as the trigger

### 7. API Gateway routes (CORS must be enabled on each)

| Method | Path | Lambda |
|---|---|---|
| DELETE | /orders/{orderId} | oms-delete-order |
| POST | /subscriptions | oms-subscribe |
| DELETE | /subscriptions | oms-unsubscribe |
| GET | /reports/deleted-orders | oms-pdf-summary |
| POST | /orders/{orderId}/translate | oms-freestyle |

Enable CORS on ALL of the above routes. Do this when creating each route, not at the end.

### 8. Freestyle UI (for Eyal to add to the web client)
On each order card, add:
- A language dropdown: Spanish (es), French (fr), German (de), Arabic (ar), Hebrew (he), Chinese (zh)
- A "Translate" button
- On click: POST /orders/{orderId}/translate with body { "targetLanguage": "<selected>" }
- Display both `originalDescription` and `translatedDescription` from the response

### 9. Important reminder — SNS email confirmation
After creating the SNS topic and running a test subscribe, check the inbox and click
"Confirm subscription". Until that is clicked, no notifications will be delivered.
Do this on Day 1 so the Day 2 delete test actually sends emails.

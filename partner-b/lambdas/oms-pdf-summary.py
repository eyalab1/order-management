import json
import boto3
import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

s3 = boto3.client('s3')
S3_BUCKET = os.environ.get('S3_BUCKET')

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,OPTIONS'
}


def lambda_handler(event, context):
    # Step 1: Get all .txt backup files from S3
    txt_files = list_backup_files()

    if not txt_files:
        return {
            'statusCode': 404,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'No deleted orders found'})
        }

    # Step 2: Read each file and parse the order data
    orders = []
    for file_key in txt_files:
        order = read_backup_file(file_key)
        orders.append(order)

    # Step 3: Build the PDF in memory
    pdf_buffer = build_pdf(orders)

    # Step 4: Upload the PDF to S3
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S')
    pdf_key = f"reports/deleted-orders-{timestamp}.pdf"

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=pdf_key,
        Body=pdf_buffer,
        ContentType='application/pdf'
    )

    # Step 5: Generate a pre-signed URL valid for 1 hour
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET, 'Key': pdf_key},
        ExpiresIn=3600
    )

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'url': url})
    }


def list_backup_files():
    response = s3.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix='deleted-orders/'
    )

    if 'Contents' not in response:
        return []

    return [
        obj['Key']
        for obj in response['Contents']
        if obj['Key'].endswith('.txt')
    ]


def read_backup_file(file_key):
    response = s3.get_object(Bucket=S3_BUCKET, Key=file_key)
    content = response['Body'].read().decode('utf-8')

    # Parse the key:value lines written by oms-stream-processor
    order = {}
    for line in content.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            order[key.strip()] = value.strip()

    return order


def build_pdf(orders):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph('Deleted Orders Summary Report', styles['Title']))
    elements.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        styles['Normal']
    ))
    elements.append(Spacer(1, 20))

    # Table header + rows
    table_data = [['Order ID', 'Description', 'Price', 'Created', 'Deleted At']]

    for order in orders:
        table_data.append([
            order.get('Order ID', ''),
            order.get('Description', ''),
            order.get('Price', ''),
            order.get('Created', ''),
            order.get('Deleted At', '')
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EEF2F5')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)

    return buffer.getvalue()

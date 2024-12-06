import boto3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from decimal import Decimal

# Initialize boto3 resources
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def lambda_handler(event, context):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    bucket_name = S3_BUCKET_NAME

    # Set the time window for querying
    now = datetime.utcnow()
    ten_seconds_ago = now - timedelta(seconds=10)
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    ten_seconds_ago_str = ten_seconds_ago.strftime('%Y-%m-%d %H:%M:%S')

    # Query data from DynamoDB
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('bucket_name').eq(bucket_name) &
                               boto3.dynamodb.conditions.Key('timestamp').between(ten_seconds_ago_str, now_str)
    )
    items = response['Items']

    # Check if any items were found
    if not items:
        return {
            'statusCode': 200,
            'body': 'No data found in the last 10 seconds.'
        }

    # Extract timestamps and sizes for plotting
    timestamps = [item['timestamp'] for item in items]
    sizes = [float(item['bucket_size']) for item in items]

    timestamps_dt = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in timestamps]
    max_size = max(sizes) if sizes else 0

    # Create and save the plot
    plt.figure()
    plt.plot(timestamps_dt, sizes, label='Bucket Size Over Time', marker='o')
    plt.axhline(y=max_size, color='r', linestyle='--', label='Max Size')
    plt.xlabel('Timestamp')
    plt.ylabel('Size (bytes)')
    plt.legend()

    plot_file = '/tmp/plot.png'
    plt.savefig(plot_file)

    # Upload the plot to S3
    with open(plot_file, 'rb') as data:
        s3.put_object(Bucket=bucket_name, Key='plot.png', Body=data)

    return {
        'statusCode': 200,
        'body': 'Plot created and uploaded to S3 successfully.'
    }

import boto3
import os
import time
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')

def get_total_bucket_size(bucket_name):
    try:
        total_size = 0
        total_objects = 0
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                total_size += obj['Size']
                total_objects += 1

        return total_size, total_objects
    except Exception as e:
        print(f"Error computing total bucket size: {e}")
        return None, None

def write_to_dynamodb(bucket_name, total_size, total_objects):
    try:
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        timestamp = Decimal(str(time.time()))
        readable_time = datetime.utcfromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        
        item = {
            'bucket_name': bucket_name,
            'timestamp': readable_time,
            'bucket_size': Decimal(total_size),
            'total_objects': Decimal(total_objects)
        }
        
        table.put_item(Item=item)
        print(f"Successfully wrote size info to DynamoDB: {item}")
    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    total_size, total_objects = get_total_bucket_size(bucket_name)
    
    if total_size is not None and total_objects is not None:
        write_to_dynamodb(bucket_name, total_size, total_objects)
    else:
        print("Failed to compute total bucket size.")

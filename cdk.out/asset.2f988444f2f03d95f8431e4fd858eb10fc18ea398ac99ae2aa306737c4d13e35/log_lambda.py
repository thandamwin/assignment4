import json
import boto3
import time

def lambda_handler(event, context):
    log_client = boto3.client('logs')
    log_group_name = '/aws/lambda/s3_operation'
    log_stream_name = 's3_log'

    try:
        log_client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
    except log_client.exceptions.ResourceAlreadyExistsException:
        pass

    processed_records = []

    for record in event['Records']:
        body = json.loads(record['body'])
        if 'Message' in body:
            sns_message = json.loads(body['Message'])

            if 'Records' in sns_message:
                for s3_event in sns_message['Records']:
                    object_key = s3_event['s3']['object']['key']
                    event_name = s3_event['eventName']
                    size_delta = s3_event['s3']['object'].get('size', 0)

                    if 'ObjectRemoved' in event_name:
                        size_delta = get_object_size(log_client, log_group_name, object_key)


                    log_event = {
                        'timestamp': int(time.time() * 1000),
                        'message': json.dumps({
                            'object_name': object_key,
                            'size_delta': -size_delta if 'ObjectRemoved' in event_name else size_delta
                        })
                    }

                    log_client.put_log_events(
                        logGroupName=log_group_name,
                        logStreamName=log_stream_name,
                        logEvents=[log_event]
                    )

                    processed_records.append({
                        'object_key': object_key,
                        'size_delta': -size_delta if 'ObjectRemoved' in event_name else size_delta,
                        'event_name': event_name
                    })
            else:
                print("No 'Records' key in SNS Message, may not be an S3 event notification.")

    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Successfully processed S3 event logs.',
            'processed_records': processed_records
        })
    }
    return response

def get_object_size(log_client, log_group_name, object_key):
    query = f'fields @message | filter object_name="{object_key}" and size_delta > 0 | sort @timestamp desc | limit 1'
    start_query_response = log_client.start_query(
        logGroupName=log_group_name,
        startTime=int(time.time()) - 86400,
        endTime=int(time.time()),
        queryString=query,
    )
    query_id = start_query_response['queryId']
    time.sleep(1) 
    response = log_client.get_query_results(
        queryId=query_id
    )

    if response['results']:
        for result in response['results']:
            for field in result:
                if field['field'] == '@message':
                    log_event = json.loads(field['value'])
                    return log_event['size_delta']
    return 0
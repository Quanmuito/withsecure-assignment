import base64
import json
import os
import uuid
import time
from datetime import datetime

import boto3
from botocore.config import Config
from botocore.exceptions import EndpointConnectionError, ClientError

ENDPOINT_URL = os.environ.get('SQS_ENDPOINT_URL', 'http://localhost:4566')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'some_key_id')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'some_secret')

QUEUE_NAME = 'submissions'
STREAM_NAME = 'events'

NEW_PROCESS_EVENT = 'new_process'
NETWORK_CONNECTION_EVENT = 'network_connection'

INVALID_IP = 'not-an-ip'
INVALID_UUID = 'not-an-uuid'
INVALID_CMDL = None

MAX_NUMBER_OF_MESSAGES = 1
VISIBILITY_TIMEOUT = 300
INTERVAL = 30


def sqs_receive_messages(
    client,
    queue_url,
    max_number_of_messages=MAX_NUMBER_OF_MESSAGES,
    visibility_timeout=VISIBILITY_TIMEOUT
):
    """
    Read messages from SQS queue
    """
    try:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            VisibilityTimeout=visibility_timeout,
        )
        return response.get('Messages', [])

    except (EndpointConnectionError, ClientError):
        pass


def sqs_delete_message(client, queue_url, receipt_handle):
    """
    Delete messages from SQS queue
    """
    try:
        client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    except (EndpointConnectionError, ClientError):
        pass


def kinesis_put_records(client, records, stream_name):
    """
    Publish record to kinesis stream
    """
    try:
        response = client.put_records(
            Records=records,
            StreamName=stream_name,
        )
        print(f"FailedRecordCount: {response['FailedRecordCount']}")

    except (EndpointConnectionError, ClientError):
        pass


def is_valid_submission(submission):
    """
    Validate submission
    """
    return submission['submission_id'] != INVALID_UUID and submission['device_id'] != INVALID_UUID


def is_valid_event(event, type):
    """
    Validate event
    """
    if type == NEW_PROCESS_EVENT:
        return event['cmdl'] != INVALID_CMDL

    elif type == NETWORK_CONNECTION_EVENT:
        return event['destination_ip'] != INVALID_IP

    else:
        return False


def decode(code):
    """
    Decode the Base64 encoded bytes data to object
    """
    decoded_message = base64.b64decode(code)
    return json.loads(decoded_message.decode())


def encode(message):
    """
    Encode data to Base64 bytes
    """
    encoded_message = json.dumps(message).encode()
    return base64.b64encode(encoded_message).decode()


def get_records(message):
    """
    Get a list of records
    """
    submission = decode(message['Body'])
    records = []

    def add_records(type):
        """
        Format event to record
        """
        for event in submission['events'][type]:
            if is_valid_event(event, type):
                event['type'] = type
                event['event_id'] = str(uuid.uuid4())
                event['device_id'] = submission['device_id']
                event['time_created'] = datetime.now().isoformat()
                record = {
                    'PartitionKey': message['MessageId'],
                    'Data': encode(event)
                }
                records.append(record)

    if is_valid_submission(submission):
        add_records(NEW_PROCESS_EVENT)
        add_records(NETWORK_CONNECTION_EVENT)

    return records


def main(queue_name=QUEUE_NAME, stream_name=STREAM_NAME):
    print('Starting preprocessing component')

    config = Config(
        region_name = 'eu-west-1',
        retries = {
            'max_attempts': 3,
            'mode': 'standard'
        }
    )

    sqs_client = boto3.client(
        'sqs',
        config=config,
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    kinesis_client = boto3.client(
        'kinesis',
        config=config,
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    while True:
        print('Processing messages...')
        queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
        messages = sqs_receive_messages(sqs_client, queue_url)

        if messages:
            for message in messages:
                records = get_records(message)
                kinesis_put_records(
                    client=kinesis_client,
                    records=records,
                    stream_name=stream_name,
                )

                sqs_delete_message(sqs_client, queue_url, message['ReceiptHandle'])
                print(f"Message {message['MessageId']} has been processed and removed!")

        else:
            print('No messages received')

        time.sleep(INTERVAL)


if __name__ == '__main__':
    main()
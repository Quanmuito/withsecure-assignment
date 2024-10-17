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
    try:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            VisibilityTimeout=visibility_timeout,
        )
        return response.get('Messages', [])

    except (EndpointConnectionError, ClientError) as e:
        print(f"Error: {e}")
        pass


def sqs_delete_message(client, queue_url, receipt_handle):
    try:
        client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    except (EndpointConnectionError, ClientError) as e:
        print(f"Error: {e}")
        pass


def kinesis_put_records(client, records, stream_name):
    try:
        response = client.put_records(
            Records=records,
            StreamName=stream_name,
        )
        print(f"FailedRecordCount: {response['FailedRecordCount']}")

    except (EndpointConnectionError, ClientError) as e:
        print(f"Error: {e}")
        pass


def is_valid_submission(submission):
    return submission['submission_id'] != INVALID_UUID and submission['device_id'] != INVALID_UUID


def is_valid_event(event, type):
    if type == NEW_PROCESS_EVENT:
        return event['cmdl'] != INVALID_CMDL

    elif type == NETWORK_CONNECTION_EVENT:
        return event['destination_ip'] != INVALID_IP

    else:
        return False


def decode(code):
    decoded_message = base64.b64decode(code)
    return json.loads(decoded_message.decode())


def encode(message):
    encoded_message = json.dumps(message).encode()
    return base64.b64encode(encoded_message).decode()


def get_records(message):
    submission = decode(message['Body'])
    records = []

    def add_records(type):
        for event in submission['events'][type]:
            if is_valid_event(event, type):
                event['type'] = type
                event['event_id'] = str(uuid.uuid4())
                event['device_id'] = submission['device_id']
                event['time_created'] = datetime.now().isoformat()
                print(event)
                record = {
                    'PartitionKey': message['MD5OfBody'],
                    'Data': encode(event)
                }
                records.append(record)

    if is_valid_submission(submission):
        add_records(NEW_PROCESS_EVENT)
        add_records(NETWORK_CONNECTION_EVENT)

    print(records)

MESSAGE = {
    'MessageId': '8bcc287b-0970-e8d4-001e-a5e6a7282efc',
    'ReceiptHandle': 'evgIjUxZWJmNDI2LWRkZWUtNDg4NS1iYmYzLWE1ZWJiNWQ2MGVhMSIsICJkZXZpY2VfaWQiOiAiN2M4NWU1NzktMTQ3MS00N2Y2LWFhZTAtOGYyZWUwNzRhYzMxIiwgInRpbWVfY3JlYXRlch',
    'Body': 'eyJzdWJtaXNzaW9uX2lkIjogIjUxZWJmNDI2LWRkZWUtNDg4NS1iYmYzLWE1ZWJiNWQ2MGVhMSIsICJkZXZpY2VfaWQiOiAiN2M4NWU1NzktMTQ3MS00N2Y2LWFhZTAtOGYyZWUwNzRhYzMxIiwgInRpbWVfY3JlYXRlZCI6ICIyMDI0LTEwLTE2VDE0OjUxOjA4LjkwOTQ3NyIsICJldmVudHMiOiB7Im5ld19wcm9jZXNzIjogW3siY21kbCI6ICJub3RlcGFkLmV4ZSIsICJ1c2VyIjogImpvaG4ifSwgeyJjbWRsIjogImNhbGN1bGF0b3IuZXhlIiwgInVzZXIiOiAiYWRtaW4ifV0sICJuZXR3b3JrX2Nvbm5lY3Rpb24iOiBbeyJzb3VyY2VfaXAiOiAiMTkyLjE2OC4wLjEiLCAiZGVzdGluYXRpb25faXAiOiAiMjMuMTMuMjUyLjM5IiwgImRlc3RpbmF0aW9uX3BvcnQiOiA1NTQxM30sIHsic291cmNlX2lwIjogIjE5Mi4xNjguMC4xIiwgImRlc3RpbmF0aW9uX2lwIjogIjIzLjEzLjI1Mi4zOSIsICJkZXN0aW5hdGlvbl9wb3J0IjogMTk2OTd9XX19',
    'MD5OfBody': '4ca38114dc7ee7f7b5c2781170fd62da',
}
get_records(MESSAGE)
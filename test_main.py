import unittest
import main

VALID_SUBMISSION = {
    'submission_id': '51ebf426-ddee-4885-bbf3-a5ebb5d60ea1',
    'device_id': '7c85e579-1471-47f6-aae0-8f2ee074ac31',
    'time_created': '2024-10-16T14:51:08.909477',
    'events': {
        'new_process': [
            {'cmdl': 'notepad.exe', 'user': 'john'},
            {'cmdl': 'calculator.exe', 'user': 'admin'},
        ],
        'network_connection': [
            {'source_ip': '192.168.0.1', 'destination_ip': '23.13.252.39', 'destination_port': 55413},
            {'source_ip': '192.168.0.1', 'destination_ip': '23.13.252.39', 'destination_port': 19697},
        ]
    }
}

SUBMISSION_NO_ID = {
    'submission_id': 'not-an-uuid',
    'device_id': '7c85e579-1471-47f6-aae0-8f2ee074ac31',
    'time_created': '2024-10-16T14:51:08.909477',
    'events': {
        'new_process': [
            {'cmdl': None, 'user': 'admin'},
            {'cmdl': 'calculator.exe', 'user': 'admin'}
        ],
        'network_connection': [
            {'source_ip': '192.168.0.2', 'destination_ip': '23.13.252.39', 'destination_port': 49723},
            {'source_ip': '192.168.0.1', 'destination_ip': '23.13.252.39', 'destination_port': 57455}
        ]
    }
}

SUBMISSION_NO_DEVICE_ID = {
    'submission_id': '51ebf426-ddee-4885-bbf3-a5ebb5d60ea1',
    'device_id': 'not-an-uuid',
    'time_created': '2024-10-16T14:51:08.909477',
    'events': {
        'new_process': [
            {'cmdl': 'notepad.exe', 'user': 'evil-guy'},
            {'cmdl': None, 'user': 'admin'},
        ],
        'network_connection': [
            {'source_ip': '192.168.0.2', 'destination_ip': '23.13.252.39', 'destination_port': 24153},
            {'source_ip': '192.168.0.2', 'destination_ip': '23.13.252.39', 'destination_port': 49723},
        ]
    }
}

VALID_NEW_PROCESS_EVENT = {
    'cmdl': 'notepad.exe',
    'user': 'evil-guy'
}

INVALID_NEW_PROCESS_EVENT = {
    'cmdl': None,
    'user': 'evil-guy'
}

VALID_NETWORK_CONNECTION_EVENT = {
    'source_ip': '192.168.0.2',
    'destination_ip': '23.13.252.39',
    'destination_port': 24153
}

INVALID_NETWORK_CONNECTION_EVENT = {
    'source_ip': '192.168.0.2',
    'destination_ip': 'not-an-ip',
    'destination_port': 24153
}

MESSAGE = {
    'MessageId': '8bcc287b-0970-e8d4-001e-a5e6a7282efc',
    'ReceiptHandle': 'evgIjUxZWJmNDI2LWRkZWUtNDg4NS1iYmYzLWE1ZWJiNWQ2MGVhMSIsICJkZXZpY2VfaWQiOiAiN2M4NWU1NzktMTQ3MS00N2Y2LWFhZTAtOGYyZWUwNzRhYzMxIiwgInRpbWVfY3JlYXRlch',
    'Body': 'eyJzdWJtaXNzaW9uX2lkIjogIjUxZWJmNDI2LWRkZWUtNDg4NS1iYmYzLWE1ZWJiNWQ2MGVhMSIsICJkZXZpY2VfaWQiOiAiN2M4NWU1NzktMTQ3MS00N2Y2LWFhZTAtOGYyZWUwNzRhYzMxIiwgInRpbWVfY3JlYXRlZCI6ICIyMDI0LTEwLTE2VDE0OjUxOjA4LjkwOTQ3NyIsICJldmVudHMiOiB7Im5ld19wcm9jZXNzIjogW3siY21kbCI6ICJub3RlcGFkLmV4ZSIsICJ1c2VyIjogImpvaG4ifSwgeyJjbWRsIjogImNhbGN1bGF0b3IuZXhlIiwgInVzZXIiOiAiYWRtaW4ifV0sICJuZXR3b3JrX2Nvbm5lY3Rpb24iOiBbeyJzb3VyY2VfaXAiOiAiMTkyLjE2OC4wLjEiLCAiZGVzdGluYXRpb25faXAiOiAiMjMuMTMuMjUyLjM5IiwgImRlc3RpbmF0aW9uX3BvcnQiOiA1NTQxM30sIHsic291cmNlX2lwIjogIjE5Mi4xNjguMC4xIiwgImRlc3RpbmF0aW9uX2lwIjogIjIzLjEzLjI1Mi4zOSIsICJkZXN0aW5hdGlvbl9wb3J0IjogMTk2OTd9XX19',
    'MD5OfBody': '4ca38114dc7ee7f7b5c2781170fd62da',
}

class TestMain(unittest.TestCase):

    def test_is_valid_submission(self):
        self.assertTrue(main.is_valid_submission(VALID_SUBMISSION))
        self.assertFalse(main.is_valid_submission(SUBMISSION_NO_ID))
        self.assertFalse(main.is_valid_submission(SUBMISSION_NO_DEVICE_ID))


    def test_is_valid_event(self):
        self.assertTrue(main.is_valid_event(VALID_NEW_PROCESS_EVENT, main.NEW_PROCESS_EVENT))
        self.assertTrue(main.is_valid_event(VALID_NETWORK_CONNECTION_EVENT, main.NETWORK_CONNECTION_EVENT))
        self.assertFalse(main.is_valid_event(INVALID_NEW_PROCESS_EVENT, main.NEW_PROCESS_EVENT))
        self.assertFalse(main.is_valid_event(INVALID_NETWORK_CONNECTION_EVENT, main.NETWORK_CONNECTION_EVENT))


    def test_decode(self):
        self.assertEqual(main.decode('InRlc3Qgc3RyaW5nIg=='), 'test string')
        self.assertEqual(main.decode('eyJjbWRsIjogIm5vdGVwYWQuZXhlIiwgInVzZXIiOiAiZXZpbC1ndXkifQ=='), {'cmdl': 'notepad.exe', 'user': 'evil-guy'})


    def test_encode(self):
        self.assertEqual(main.encode('test string'), 'InRlc3Qgc3RyaW5nIg==')
        self.assertEqual(main.encode({'cmdl': 'notepad.exe', 'user': 'evil-guy'}), 'eyJjbWRsIjogIm5vdGVwYWQuZXhlIiwgInVzZXIiOiAiZXZpbC1ndXkifQ==')


    def test_get_records(self):
        records = main.get_records(MESSAGE)
        for record in records:
            self.assertEqual(record['PartitionKey'], MESSAGE['MessageId'])
            event = main.decode(record['Data'])
            self.assertIsNotNone(event['type'])
            self.assertIsNotNone(event['event_id'])
            self.assertIsNotNone(event['device_id'])
            self.assertIsNotNone(event['time_created'])


if __name__ == '__main__':
    unittest.main()
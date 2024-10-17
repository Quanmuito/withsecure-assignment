# Withsecure assignment submission

## Description
This is a simple preprocessing for an EDR backend that processes telementry submissions from sensors to SQS and publishes data to Kinesis stream.

### Main functions

* Every 30 seconds, the component reads messages from SQS queue, formats data and publishes events to Kinesis stream.
* The read messages will be deleted after all events are published to Kinesis stream.

### Requirements

* each event is published as an individual record to kinesis (one submission is turned into multiple events) ✔️
* each event must have information of the event type (`new_process` or `network_connection`) ✔️
* each event must have an unique identifier ✔️
* each event must have an identifier of the source device (`device_id`) ✔️
* each event must have a timestamp when it was processed (backend side time in UTC) ✔️
* submissions are validated and invalid or broken submissions are dropped ✔️
* must guarantee no data loss (for valid data), i.e. submissions must not be deleted before all events are succesfully published ✔️
* must guarantee ordering of events in the context of a single submission ✔️
* the number of messages read from SQS with a single request must be configurable ✔️
* the visibility timeout of read SQS messages must be configurable ✔️

### Optional design questions

* Q: How does your application scale and guarantee near-realtime processing when the incoming traffic increases?
* A: My application can be scaled up by increase MAX_NUMBER_OF_MESSAGES to read more message at once and reducing the INTERVAL to make it processes submissions from SQS more frequent.

* Where are the possible bottlenecks and how to tackle those?
* A: One possible bottlenecks would be 'receive_messages' method returns maximum 10 messages with or 'put_records' method support up to 500 records each request.
* In order to solve this, I can set up more queue and more data stream, then set up the software to watch each queue and stream pair.

* What kind of metrics you would collect from the application to get visibility to its througput, performance and health?
* I would collect number of messages read and number of events published within a period of time to asset the throughput and performance of the software. In addition, I would collect the number of submissions from sensors to adjust the interval and solve possible bottlenecks.

* Q: How would you deploy your application in a real world scenario?
* A: In a real world scenario, I would depoy it as a microservice to format data from SQS before published to Kinesis to be analyzed.

* Q: What kind of testing, deployment stages or quality gates you would build to ensure a safe production deployment?
* A: I followed Single Responsibility Principle and write unit tests like 'test_main.py' file. In real world, I would set up some jobs to run those tests on a CI (for example with Github Actions).
* I prefer 3 steps of testing before deploy to production.
    - 1st step - Development stage: The person that review the PR should test the application with his/her local environment.
    - 2nd step - Staging stage: The application should be deployed to an UAT server (a server that mimic production but for testing purpose) or a replicated server and let testers work on it.
    - 3rd step - Production stage: The application deployed to production environment.

## Setup
### Prerequisite
Follow instruction to set up the environment that includes mock AWS with localstack and mock sensor-fleet.

### Running the services

Once the environment is up, open a terminal at this folder and use command `docker-compose up -d`.

To access the records that published to Kinesis, open the terminal that start the environment, run these commands by order and expect similar response as example below:

Get stream name
```console
$ docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis list-streams
{
    "StreamNames": [
        "events"
    ]
}
```

Get the steam details, in this case we look at the stream named 'events' and get shard id
```console
$ docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis describe-stream --stream-name events
{
    "StreamDescription": {
        "Shards": [
            {
                "ShardId": "shardId-000000000000",
                "HashKeyRange": {
                    "StartingHashKey": "0",
                    "EndingHashKey": "170141183460469231731687303715884105726"
                },
                "SequenceNumberRange": {
                    "StartingSequenceNumber": "49656829339014114656691664164803771812684910269690806274"
                }
            },
            {
                "ShardId": "shardId-000000000001",
                "HashKeyRange": {
                    "StartingHashKey": "170141183460469231731687303715884105727",
                    "EndingHashKey": "340282366920938463463374607431768211455"
                },
                "SequenceNumberRange": {
                    "StartingSequenceNumber": "49656829339036415401890194787945307530957558631196786706"
                }
            }
        ],
        "StreamARN": "arn:aws:kinesis:eu-west-1:000000000000:stream/events",
        "StreamName": "events",
        "StreamStatus": "ACTIVE",
        "RetentionPeriodHours": 24,
        "EnhancedMonitoring": [
            {
                "ShardLevelMetrics": []
            }
        ],
        "EncryptionType": "NONE",
        "KeyId": null,
        "StreamCreationTimestamp": 1729123920.896
    }
}
```

Copy 1 shard_id and replace with 'shard_id_here' to get the 'ShardIterator'
```console
$ docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis get-shard-iterator \
    --stream-name events \
    --shard-id shard_id_here \
    --shard-iterator-type TRIM_HORIZON
{
    "ShardIterator": "AAAAAAAAAAG3mIJ4m4mybniNFm/2IWs16Tk/tVRyegqqulx4GXTQ+O4lpVHzUtAwRrwrhQcGKzyFVi8YpVGnjfIPfEIGAVT1ZunbNqqsjLCjiQ4P2VmjhmQR+76MvBqtHHPi8V9ANTA0Wl7AxxFqe6vpqGASaY61E2ysiTPZBlt2IeFMcujDKpM43kyhhTnw+0Iw9Lyzs2U="
}
```

Copy the ShardIterator value and replace with 'shard_iterator_here' to see records
```console
$ docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis get-records \
    --shard-iterator shard_iterator_here
{
    "Records": [
        {
            "SequenceNumber": "49656829339036415401890194788346670903069638263346036754",
            "ApproximateArrivalTimestamp": 1729124251.866,
            "Data": "ZX...PQ==",
            "PartitionKey": "ebc79bb3af4aa0ad8bfca1f8a1646e08",
            "EncryptionType": "NONE"
        },
        {
            "SequenceNumber": "49656829339036415401890194788347879828889252892520742930",
            "ApproximateArrivalTimestamp": 1729124251.866,
            "Data": "ZX...PQ==",
            "PartitionKey": "ebc79bb3af4aa0ad8bfca1f8a1646e08",
            "EncryptionType": "NONE"
        }
        ...
    ],
    "NextShardIterator": "AAAAAAAAAAGgj+YVmtU22yN6zCo/jKUZp7rLdFpw2evT1U/0jg6EKs1vnacbRsTKG7ZU0pwWjIt5Co1iiaRj/peVPBaj0kl+5udiGtqrzs8Rohok9RxRSavaU0R3jYK0HO0uTbFMV47tacgXc+5JDKmw3uhoRwEHWwW61jnRmGSEq4GaRlVi0bZq3IyMVbgolzjKy25i3Vs=",
    "MillisBehindLatest": 0,
    "ChildShards": []
}
```

Should you have any problems with the environment or the service, you can fully reset it by executing `docker-compose down` and then `docker-compose up -d`.

### Data format

new_process event data follow this JSON format:

```yaml
{
    "cmdl": "<commandline>",                 # command line of the executed process (string)
    "user": "<username>",                    # username who started the process (string)
    "type": "new_process",                   # type identifier of the event (string)
    "event_id": "<uuid>",                    # unique identifier of the event (string)
    "device_id": "<uuid>",                   # unique identifier of the device (string)
    "time_created": "<ISO 8601>"             # creation time of the event, backend time (string)
}
```

network_connection event data follow this JSON format:

```yaml
{
    "source_ip": "<ipv4>",                   # source ip of the network connection, e.g. "192.168.0.1" (string)
    "destination_ip": "<ipv4>",              # destination ip of the network connection, e.g. "142.250.74.110" (string)
    "destination_port": <0-65535>,           # destination port of the network connection, e.g. 443 (integer)
    "type": "new_process",                   # type identifier of the event (string)
    "event_id": "<uuid>",                    # unique identifier of the event (string)
    "device_id": "<uuid>",                   # unique identifier of the device (string)
    "time_created": "<ISO 8601>"             # creation time of the event, backend time (string)
}
```
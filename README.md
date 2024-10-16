docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis describe-stream --stream-name events

docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis get-shard-iterator \
    --stream-name events \
    --shard-id shardId-000000000000 \
    --shard-iterator-type TRIM_HORIZON

docker-compose exec localstack aws --endpoint-url=http://localhost:4566 kinesis get-records \
    --shard-iterator <shard_iterator>
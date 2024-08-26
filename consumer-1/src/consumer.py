import requests
import json

# Kafka Connect REST API URL
KAFKA_CONNECT_URL = "http://localhost:8083/connectors"

# AWS S3 and Kafka topic configurations
s3_bucket_name = "<Your S3 Bucket Name>"
aws_region = "<Your AWS Region>"
kafka_topic = "<Your Kafka Topic>"
partition_field = "<Field to Partition On>"  # e.g., "year", "month", "day"

# Connector configuration
config = {
    "name": "s3-sink-connector",
    "config": {
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "tasks.max": "1",
        "topics": kafka_topic,
        "s3.bucket.name": s3_bucket_name,
        "s3.region": aws_region,
        "s3.part.size": "5242880",  # 5 MB
        "flush.size": "1000",
        "storage.class": "io.confluent.connect.s3.storage.S3Storage",
        "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
        "partitioner.class": "io.confluent.connect.storage.partitioner.FieldPartitioner",
        "partition.field.name": partition_field,
        "schema.compatibility": "NONE",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false",
        "key.converter.schemas.enable": "false"
    }
}

# Create the connector
headers = {
    "Content-Type": "application/json"
}

response = requests.post(KAFKA_CONNECT_URL, headers=headers, data=json.dumps(config))

if response.status_code == 201:
    print("Connector created successfully.")
elif response.status_code == 409:
    print("Connector already exists.")
else:
    print(f"Failed to create connector: {response.content.decode()}")

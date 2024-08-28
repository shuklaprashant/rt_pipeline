import logging
import os
import json
from datetime import datetime
import time
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kafka configurations
KAFKA_TOPIC = [os.environ.get("KAFKA_TOPIC", None)]
KAFKA_BOOTSTRAP_SERVER = os.environ.get("KAFKA_BOOTSTRAP_SERVER", None)
KAFKA_SCHEMA_REGISTRY_URL = os.environ.get("KAFKA_SCHEMA_REGISTRY_URL", 'http://localhost:8081')

# S3 configurations
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", None)
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", None)
AWS_REGION = os.environ.get("AWS_REGION", None)
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", None)

# Initialize Kafka Consumer
consumer_conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
    'group.id': 2,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    # 'schema.registry.url': KAFKA_SCHEMA_REGISTRY_URL
}

logger.info("Initializing Kafka AvroConsumer.")
# consumer = AvroConsumer(consumer_conf)
consumer = Consumer(consumer_conf)
consumer.subscribe(KAFKA_TOPIC)

schema_registry_client = SchemaRegistryClient({'url': KAFKA_SCHEMA_REGISTRY_URL})

avro_deserializer = AvroDeserializer(schema_registry_client)

# Initialize S3 client
logger.info("Initializing S3 client.")
s3_client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY)

def process_and_upload_to_s3(message):
    logger.debug("Processing message: %s", message)
    
    timestamp_epoch = message.get('at_time', None)
    
    if timestamp_epoch:
        # Convert epoch to datetime
        timestamp = datetime.fromtimestamp(timestamp_epoch)

        # Create folder structure based on timestamp
        year = timestamp.strftime('%Y')
        month = str(int(timestamp.strftime('%m')))  # Removing leading zeros
        day = str(int(timestamp.strftime('%d')))  # Removing leading zeros
        hour = timestamp.strftime('%H')
        minute = timestamp.strftime('%M')
        second = timestamp.strftime('%S')

        # Create folder path
        folder_path = f"{year}/{month}/{day}"

        # Create file name (e.g., 01.json)
        file_name = f"Page_View_Event_{hour}-{minute}-{second}.json"

        # Full S3 path
        s3_path = os.path.join(folder_path, file_name)

        try:
            # Uploading data to S3
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_path,
                Body=json.dumps(message)  # Assuming you're storing the message as JSON
            )
            logger.info(f"Uploaded to S3: {s3_path}")
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
    else:
        logger.warning("Timestamp not found in message.")

def consume():
    msg_count = 0
    logger.info("Starting message consumption from Kafka topic: %s", KAFKA_TOPIC)

    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                logger.info('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
            else:
                logger.error('Error occurred: {0}'.format(msg.error().str()))
            continue
        
        event = avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))

        logger.debug("Received message: %s", event)
        process_and_upload_to_s3(event)
        msg_count += 1
        if msg_count % 2 == 0:
            logger.info("Committing offset after processing %d messages.", msg_count)
            consumer.commit(asynchronous=True)

if __name__ == "__main__":
    try:
        time.sleep(60)
        consume()
    except Exception as e:
        logger.error(f"An error occurred in the consumer: {e}")
    finally:
        consumer.close()
        logger.info("Consumer closed.")

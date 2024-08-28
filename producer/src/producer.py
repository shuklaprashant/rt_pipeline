import os
from uuid import uuid4
import json
import logging

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from websocket import create_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def record_to_dict(record, ctx):
    return json.loads(record)


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred or None on success.

        msg (Message): The message that was produced or failed.
    """
    if err is not None:
        logger.error("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    logger.info('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def main():
    topic = 'page_views'

    # Load schema
    schema_path = os.environ.get("SCHEMA_FILE_LOCATION", None)
    if not schema_path or not os.path.exists(schema_path):
        logger.error("Schema file not found at {}".format(schema_path))
        return

    logger.info("Loading schema from {}".format(schema_path))
    with open(schema_path, "r") as f:
        schema_str = f.read()
    
    schema_registry_conf = {'url': os.environ.get("KAFKA_SCHEMA_REGISTRY_URL", 'http://localhost:8081')}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema_str,
                                     record_to_dict)

    string_serializer = StringSerializer('utf_8')

    producer_conf = {'bootstrap.servers': os.environ.get("KAFKA_BOOTSTRAP_SERVER", 'localhost:9092')}

    logger.info("Initializing Kafka producer with configuration: {}".format(producer_conf))
    producer = Producer(producer_conf)

    logger.info("Producing user records to topic {}. Press ^C to exit.".format(topic))

    # Connect to WebSocket server
    try:
        logger.info("Connecting to WebSocket server at ws://rt-simulator:5678")
        ws_connection = create_connection('ws://rt-simulator:5678')
    except Exception as e:
        logger.error("Failed to connect to WebSocket server: {}".format(e))
        return

    try:
        payload = ws_connection.recv()
        while payload:
            payload_utf8 = payload.decode()
            record_json = json.loads(payload_utf8)
            logger.info("Inserting Event for user_id: {}".format(record_json.get("user_id", "Unknown")))

            producer.produce(topic=topic,
                             key=string_serializer(str(uuid4())),
                             value=avro_serializer(payload_utf8, SerializationContext(topic, MessageField.VALUE)),
                             on_delivery=delivery_report)
            producer.poll(1)
            payload = ws_connection.recv()

    except Exception as e:
        logger.error("Error during message production: {}".format(e))

    finally:
        logger.info("Flushing records...")
        producer.flush()

        logger.info("Closing WebSocket connection.")
        ws_connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Program interrupted. Exiting.")
    except Exception as e:
        logger.error("An error occurred: {}".format(e))

import os
from uuid import uuid4
import json

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from websocket import create_connection

PRODUCER_MAX_SLEEP_TIME_SECONDS = int(os.environ.get("PRODUCER_MAX_SLEEP_TIME_SECONDS", None))

def record_to_dict(record, ctx):
    return json.loads(record)


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.

        msg (Message): The message that was produced or failed.

    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def main():
    topic = 'incident'

    schema_path = os.environ.get("SCHEMA_FILE_LOCATION", None)
    with open(schema_path, "r") as f:
        schema_str = f.read()
    
    schema_registry_conf = {'url': os.environ.get("KAFKA_SCHEMA_REGISTRY_URL", 'http://localhost:8081')}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema_str,
                                     record_to_dict)

    string_serializer = StringSerializer('utf_8')

    producer_conf = {'bootstrap.servers': os.environ.get("KAFKA_BOOTSTRAP_SERVER", 'localhost:9092')}

    producer = Producer(producer_conf)

    print("Producing user records to topic {}. ^C to exit.".format(topic))

    ws_connection = create_connection('ws://lfb-rt-simulator:5678')
    payload = ws_connection.recv()
    while payload:
        payload_utf8 = payload.decode()
        record_json = json.loads(payload_utf8)
        print("Inserting IncidentNumber={IncidentNumber}".format(IncidentNumber=record_json["IncidentNumber"]))
        producer.produce(topic=topic,
                             key=string_serializer(str(uuid4())),
                             value=avro_serializer(payload_utf8, SerializationContext(topic, MessageField.VALUE)),
                             on_delivery=delivery_report)
        producer.poll(1)
        # time.sleep(5)
        payload =  ws_connection.recv()

    print("\nFlushing records...")
    producer.flush()

if __name__ == '__main__':

    main()
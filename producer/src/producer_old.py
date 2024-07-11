import csv
import gzip
import json
import os
import io
import time
import avro.schema
from avro.io import DatumWriter
from confluent_kafka import Producer, avro

schema_path = os.environ.get("SCHEMA_FILE_LOCATION", None)
with open(schema_path, "r") as f:
    schema_str = f.read()

schema = avro.loads(schema_str)

producer_config = {
    'bootstrap.servers': os.environ.get("KAFKA_BOOTSTRAP_SERVER", 'localhost:9092'),
    'schema.registry.url': os.environ.get("KAFKA_SCHEMA_REGISTRY_URL", 'http://localhost:8081'),
    'client.id': 'csv-producer'
}

avro_producer = avro.AvroProducer(producer_config, default_value_schema=schema)

topic = 'incident'

CSV_FILE_LOCATION = os.environ.get("CSV_FILE_LOCATION", None)
PRODUCER_MAX_SLEEP_TIME_SECONDS = int(os.environ.get("PRODUCER_MAX_SLEEP_TIME_SECONDS", None))

def acked(err, msg):
    if err is not None:
        print(f"Failed to deliver message: {err}")
    else:
        print(f"Message produced: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

with gzip.open(CSV_FILE_LOCATION, mode="rt", encoding="utf-8-sig") as gzip_file:
    dict_stream = csv.DictReader(gzip_file, delimiter=",")

    for row in dict_stream:
        
        avro_record = {
            'IncidentNumber': row['IncidentNumber'],
            'DateOfCall': row['DateOfCall'],
            'CalYear': row['CalYear'],
            'TimeOfCall': row['TimeOfCall'],
            'HourOfCall': row['HourOfCall'],
            'IncidentGroup': row['IncidentGroup'],
            'IncidentStationGround': row['IncidentStationGround'],
            'FirstPumpArriving_AttendanceTime': row['FirstPumpArriving_AttendanceTime'] if row['FirstPumpArriving_AttendanceTime'] else None
        }
        print(avro_record)

        avro_producer.produce(topic=topic, value=avro_record, callback=acked)

        time.sleep(PRODUCER_MAX_SLEEP_TIME_SECONDS)

        avro_producer.poll(1)

avro_producer.flush()

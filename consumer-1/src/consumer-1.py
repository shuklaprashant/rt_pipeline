from confluent_kafka import Consumer, KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from pymongo import MongoClient, UpdateOne
import os

class KafkaMongoConsumer:
    def __init__(self, kafka_brokers, group_id, schema_registry_url, mongodb_uri, db_name, topics, topic_to_collection, key_fields, value_fields):
        self.consumer_conf = {
            'bootstrap.servers': kafka_brokers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'schema.registry.url': schema_registry_url
        }

        self.consumer = AvroConsumer(self.consumer_conf)
        self.consumer.subscribe(topics)

        self.mongo_client = MongoClient(mongodb_uri)
        self.mongo_db = self.mongo_client[db_name]

        self.collections = {topic: self.mongo_db[collection_name] for topic, collection_name in topic_to_collection.items()}
        self.key_fields = key_fields
        self.value_fields = value_fields

        self.messages = {}

    def consume(self):
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
                else:
                    print('Error occurred: {0}'.format(msg.error().str()))
                continue

            topic = msg.topic()
            if topic not in self.messages:
                self.messages[topic] = []

            self.messages[topic].append(msg.value())
            self.update_mongodb_collection(topic, msg)

    def update_mongodb_collection(self, topic, msg):
        if topic not in self.collections:
            print(self.collections)
            print(f"No collection mapped for topic: {topic}")
            return

        collection = self.collections[topic]
        bulk_operations = []

        key_dict = {field: msg.key()[field] for field in self.key_fields[topic]}
        value_dict = {f"$set": {field: msg.value()[field] for field in self.value_fields[topic]}}

        bulk_operations.append(
            UpdateOne(
                key_dict,
                value_dict,
                upsert=True
            )
        )

        if bulk_operations:
            collection.bulk_write(bulk_operations)
            print(f"Inserted aggregated data to MongoDB collection: {collection.name}")

if __name__ == '__main__':
    kafka_brokers = os.environ.get('KAFKA_BOOTSTRAP_SERVER', 'localhost:19092')
    group_id = 'group-1'
    schema_registry_url = os.environ.get('KAFKA_SCHEMA_REGISTRY_URL', 'http://schema-registry:8081')
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = 'page_views'
    topics = [
              'PAGE_VIWES_COUNT'
              ]
    
    topic_to_collection = {
        'PAGE_VIEWS_COUNT': 'PAGE_VIEWS_COUNT'
    }

    key_fields = {
        'PAGE_VIEWS_COUNT': ['POSTCODE', 'WINDOWSTART', 'WINDOWEND']
    }

    value_fields = {
        'PAGE_VIEWS_COUNT': ['TOTAL_VIEWS']
    }

    kafka_mongo_consumer = KafkaMongoConsumer(kafka_brokers, group_id, schema_registry_url, mongodb_uri, db_name, topics, topic_to_collection, key_fields, value_fields)

    try:
        kafka_mongo_consumer.consume()
    except KeyboardInterrupt:
        pass
    finally:
        kafka_mongo_consumer.consumer.close()
        
from confluent_kafka import Producer
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

conf = {
    "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP"],
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "PLAIN",
    "sasl.username": os.environ["CONFLUENT_API_KEY"],
    "sasl.password": os.environ["CONFLUENT_API_SECRET"],
    "linger.ms": 10,
}

producer = Producer(conf)

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_item(topic, item):
    producer.produce(
        topic=topic,
        key=item["item_url"],
        value=json.dumps(item, default=json_serializer),
        on_delivery=delivery_report
    )
    producer.poll(0)
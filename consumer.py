from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "automq-test",
    bootstrap_servers='127.0.0.1:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='automq-group'
)

print("Waiting for messages...\n")
for message in consumer:
    print(f"Received: {message.value}")

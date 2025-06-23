from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "automq-topic",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id="automq-group"
)

print("Listening for messages...")
for msg in consumer:
    print("Received:", msg.value)

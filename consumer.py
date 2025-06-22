from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='test-group'
)

print("Consumer started. Listening to topic...")

for msg in consumer:
    print(f"Received: {msg.value.decode('utf-8')}")

from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='127.0.0.1:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all'
)

topic = "automq-test"

for i in range(10):
    msg = {"id": i, "message": f"Hello AutoMQ #{i}"}
    producer.send(topic, value=msg)
    print(f"Sent: {msg}")
    time.sleep(1)

producer.flush()
producer.close()

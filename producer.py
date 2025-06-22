from kafka import KafkaProducer
import time

producer = KafkaProducer(bootstrap_servers='localhost:9092')

for i in range(10):
    msg = f"Test message {i}"
    producer.send('test-topic', msg.encode('utf-8'))
    print(f"Sent: {msg}")
    time.sleep(1)

producer.flush()
producer.close()

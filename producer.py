# producer.py
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
import threading
import psutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self, bootstrap_servers=['localhost:9092'], topic='test-events'):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # Performance optimizations
            batch_size=16384,
            linger_ms=10,
            compression_type='snappy',
            max_in_flight_requests_per_connection=5,
            acks='all',
            retries=3
        )
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
    def generate_event(self, event_type="user_action"):
        """Generate different types of events"""
        event_types = {
            "user_action": {
                "event_type": "user_action",
                "user_id": random.randint(1000, 9999),
                "action": random.choice(["click", "view", "purchase", "login", "logout"]),
                "page": random.choice(["home", "product", "cart", "checkout", "profile"]),
                "timestamp": datetime.now().isoformat(),
                "session_id": f"session_{random.randint(100000, 999999)}",
                "device": random.choice(["mobile", "desktop", "tablet"]),
                "location": random.choice(["US", "UK", "CA", "AU", "DE"])
            },
            "system_metric": {
                "event_type": "system_metric",
                "metric_name": random.choice(["cpu_usage", "memory_usage", "disk_io", "network_io"]),
                "value": round(random.uniform(0, 100), 2),
                "timestamp": datetime.now().isoformat(),
                "host": f"server-{random.randint(1, 10)}",
                "datacenter": random.choice(["us-east-1", "us-west-2", "eu-west-1"])
            },
            "transaction": {
                "event_type": "transaction",
                "transaction_id": f"txn_{random.randint(100000, 999999)}",
                "amount": round(random.uniform(10, 1000), 2),
                "currency": random.choice(["USD", "EUR", "GBP", "CAD"]),
                "merchant": random.choice(["Amazon", "Shopify", "PayPal", "Stripe"]),
                "timestamp": datetime.now().isoformat(),
                "status": random.choice(["completed", "pending", "failed"])
            }
        }
        return event_types.get(event_type, event_types["user_action"])
    
    def send_message(self, message, key=None):
        """Send a single message"""
        try:
            future = self.producer.send(self.topic, value=message, key=key)
            future.add_callback(self.on_success)
            future.add_errback(self.on_error)
            return future
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.error_count += 1
    
    def on_success(self, record_metadata):
        self.message_count += 1
        if self.message_count % 100 == 0:
            elapsed = time.time() - self.start_time
            rate = self.message_count / elapsed
            logger.info(f"Sent {self.message_count} messages. Rate: {rate:.2f} msg/sec")
    
    def on_error(self, exception):
        self.error_count += 1
        logger.error(f"Error sending message: {exception}")
    
    def produce_batch(self, count=1000, delay=0.01):
        """Produce a batch of messages"""
        logger.info(f"Starting to produce {count} messages...")
        
        for i in range(count):
            # Generate different types of events
            event_type = random.choice(["user_action", "system_metric", "transaction"])
            event = self.generate_event(event_type)
            
            # Use event type as key for partitioning
            key = event_type
            
            self.send_message(event, key)
            
            if delay > 0:
                time.sleep(delay)
        
        # Flush remaining messages
        self.producer.flush()
        
        elapsed = time.time() - self.start_time
        logger.info(f"Produced {self.message_count} messages in {elapsed:.2f} seconds")
        logger.info(f"Average rate: {self.message_count/elapsed:.2f} messages/second")
        logger.info(f"Errors: {self.error_count}")
    
    def produce_continuous(self, rate_per_second=100):
        """Produce messages continuously at specified rate"""
        logger.info(f"Starting continuous production at {rate_per_second} msg/sec")
        
        delay = 1.0 / rate_per_second
        
        try:
            while True:
                event_type = random.choice(["user_action", "system_metric", "transaction"])
                event = self.generate_event(event_type)
                self.send_message(event, event_type)
                time.sleep(delay)
        except KeyboardInterrupt:
            logger.info("Stopping producer...")
            self.producer.flush()
            self.producer.close()
    
    def get_stats(self):
        """Get producer statistics"""
        elapsed = time.time() - self.start_time
        return {
            "messages_sent": self.message_count,
            "errors": self.error_count,
            "elapsed_time": elapsed,
            "messages_per_second": self.message_count / elapsed if elapsed > 0 else 0
        }
    
    def close(self):
        """Close producer"""
        self.producer.flush()
        self.producer.close()

# Example usage
if __name__ == "__main__":
    producer = EventProducer()
    
    # Choose mode
    mode = input("Choose mode (batch/continuous): ").lower()
    
    if mode == "batch":
        count = int(input("Enter number of messages to send (default 1000): ") or 1000)
        producer.produce_batch(count)
    elif mode == "continuous":
        rate = int(input("Enter messages per second (default 100): ") or 100)
        producer.produce_continuous(rate)
    else:
        print("Invalid mode. Using batch mode...")
        producer.produce_batch(1000)
    
    stats = producer.get_stats()
    print(f"\nFinal Stats: {stats}")
    producer.close()
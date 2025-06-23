# consumer.py
import json
import time
import threading
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import logging
from collections import defaultdict, deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventConsumer:
    def __init__(self, bootstrap_servers=['localhost:9092'], topics=['test-events'], group_id='event-processor'):
        self.topics = topics
        self.group_id = group_id
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
            key_deserializer=lambda m: m.decode('utf-8') if m else None,
            # Performance settings
            max_poll_records=500,
            session_timeout_ms=30000,
            heartbeat_interval_ms=3000,
            fetch_max_wait_ms=500
        )
        
        # Statistics
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()
        self.event_counts = defaultdict(int)
        self.latency_samples = deque(maxlen=1000)
        self.processing_times = deque(maxlen=1000)
        
        # Processing handlers
        self.event_handlers = {
            'user_action': self.handle_user_action,
            'system_metric': self.handle_system_metric,
            'transaction': self.handle_transaction
        }
    
    def handle_user_action(self, event):
        """Process user action events"""
        user_id = event.get('user_id')
        action = event.get('action')
        page = event.get('page')
        
        # Simulate processing
        time.sleep(0.001)  # 1ms processing time
        
        logger.debug(f"User {user_id} performed {action} on {page}")
        return f"Processed user action: {action}"
    
    def handle_system_metric(self, event):
        """Process system metric events"""
        metric_name = event.get('metric_name')
        value = event.get('value')
        host = event.get('host')
        
        # Simulate processing
        time.sleep(0.002)  # 2ms processing time
        
        logger.debug(f"System metric {metric_name}: {value} from {host}")
        return f"Processed metric: {metric_name}"
    
    def handle_transaction(self, event):
        """Process transaction events"""
        txn_id = event.get('transaction_id')
        amount = event.get('amount')
        status = event.get('status')
        
        # Simulate processing
        time.sleep(0.003)  # 3ms processing time
        
        logger.debug(f"Transaction {txn_id}: ${amount} - {status}")
        return f"Processed transaction: {txn_id}"
    
    def calculate_latency(self, event):
        """Calculate end-to-end latency"""
        try:
            event_timestamp = datetime.fromisoformat(event.get('timestamp', ''))
            current_timestamp = datetime.now()
            latency = (current_timestamp - event_timestamp).total_seconds() * 1000  # ms
            self.latency_samples.append(latency)
            return latency
        except:
            return None
    
    def process_message(self, message):
        """Process a single message"""
        start_time = time.time()
        
        try:
            event = message.value
            event_type = event.get('event_type', 'unknown')
            
            # Calculate latency
            latency = self.calculate_latency(event)
            
            # Route to appropriate handler
            handler = self.event_handlers.get(event_type, self.handle_unknown)
            result = handler(event)
            
            # Update statistics
            self.message_count += 1
            self.event_counts[event_type] += 1
            
            processing_time = (time.time() - start_time) * 1000  # ms
            self.processing_times.append(processing_time)
            
            if self.message_count % 100 == 0:
                self.print_stats()
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing message: {e}")
            return None
    
    def handle_unknown(self, event):
        """Handle unknown event types"""
        logger.warning(f"Unknown event type: {event.get('event_type')}")
        return "Processed unknown event"
    
    def print_stats(self):
        """Print current statistics"""
        elapsed = time.time() - self.start_time
        rate = self.message_count / elapsed if elapsed > 0 else 0
        
        avg_latency = sum(self.latency_samples) / len(self.latency_samples) if self.latency_samples else 0
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        logger.info(f"Processed: {self.message_count} | Rate: {rate:.2f} msg/sec | "
                   f"Avg Latency: {avg_latency:.2f}ms | Avg Processing: {avg_processing_time:.2f}ms")
    
    def consume_batch(self, max_messages=1000, timeout_ms=30000):
        """Consume messages in batch mode"""
        logger.info(f"Starting batch consumption (max {max_messages} messages)...")
        
        consumed = 0
        start_time = time.time()
        
        try:
            while consumed < max_messages:
                message_batch = self.consumer.poll(timeout_ms=timeout_ms)
                
                if not message_batch:
                    logger.info("No messages received, continuing...")
                    continue
                
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        self.process_message(message)
                        consumed += 1
                        
                        if consumed >= max_messages:
                            break
                    
                    if consumed >= max_messages:
                        break
                
                # Check for timeout
                if time.time() - start_time > timeout_ms / 1000:
                    logger.info("Timeout reached")
                    break
            
            logger.info(f"Batch consumption completed. Processed {consumed} messages")
            
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            self.consumer.close()
    
    def consume_continuous(self):
        """Consume messages continuously"""
        logger.info("Starting continuous consumption...")
        
        try:
            for message in self.consumer:
                self.process_message(message)
                
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            self.consumer.close()
    
    def get_detailed_stats(self):
        """Get detailed statistics"""
        elapsed = time.time() - self.start_time
        
        avg_latency = sum(self.latency_samples) / len(self.latency_samples) if self.latency_samples else 0
        max_latency = max(self.latency_samples) if self.latency_samples else 0
        min_latency = min(self.latency_samples) if self.latency_samples else 0
        
        avg_processing = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        max_processing = max(self.processing_times) if self.processing_times else 0
        
        return {
            "messages_processed": self.message_count,
            "errors": self.error_count,
            "elapsed_time": elapsed,
            "messages_per_second": self.message_count / elapsed if elapsed > 0 else 0,
            "event_counts": dict(self.event_counts),
            "latency_stats": {
                "avg_ms": avg_latency,
                "max_ms": max_latency,
                "min_ms": min_latency
            },
            "processing_stats": {
                "avg_ms": avg_processing,
                "max_ms": max_processing
            }
        }

# Example usage
if __name__ == "__main__":
    consumer = EventConsumer()
    
    # Choose mode
    mode = input("Choose mode (batch/continuous): ").lower()
    
    if mode == "batch":
        max_messages = int(input("Enter max messages to consume (default 1000): ") or 1000)
        consumer.consume_batch(max_messages)
    elif mode == "continuous":
        consumer.consume_continuous()
    else:
        print("Invalid mode. Using continuous mode...")
        consumer.consume_continuous()
    
    stats = consumer.get_detailed_stats()
    print(f"\nFinal Stats: {json.dumps(stats, indent=2)}")
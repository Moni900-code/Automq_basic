# monitor.py
import time
import json
import threading
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from collections import deque
import psutil
import requests

class AutoMQMonitor:
    def __init__(self):
        self.metrics = {
            'throughput': deque(maxlen=300),  # 5 minutes of data
            'latency': deque(maxlen=300),
            'cpu_usage': deque(maxlen=300),
            'memory_usage': deque(maxlen=300),
            'timestamps': deque(maxlen=300)
        }
        self.monitoring = False
    
    def get_kafka_metrics(self):
        """Get Kafka/AutoMQ metrics via JMX or API"""
        # For demo purposes, we'll simulate metrics
        # In real scenario, you'd use JMX or AutoMQ APIs
        return {
            'messages_per_sec': 1000 + (time.time() % 100),
            'avg_latency_ms': 5 + (time.time() % 10),
            'partition_count': 3,
            'active_connections': 5
        }
    
    def get_system_metrics(self):
        """Get system resource metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters().read_bytes + psutil.disk_io_counters().write_bytes,
            'network_io': psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        }
    
    def collect_metrics(self):
        """Collect all metrics"""
        while self.monitoring:
            try:
                kafka_metrics = self.get_kafka_metrics()
                system_metrics = self.get_system_metrics()
                
                timestamp = datetime.now()
                
                self.metrics['throughput'].append(kafka_metrics['messages_per_sec'])
                self.metrics['latency'].append(kafka_metrics['avg_latency_ms'])
                self.metrics['cpu_usage'].append(system_metrics['cpu_percent'])
                self.metrics['memory_usage'].append(system_metrics['memory_percent'])
                self.metrics['timestamps'].append(timestamp)
                
                time.sleep(1)  # Collect every second
                
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                time.sleep(1)
    
    def start_monitoring(self):
        """Start monitoring in background thread"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.collect_metrics)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("Monitoring started...")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        print("Monitoring stopped.")
    
    def plot_metrics(self):
        """Plot collected metrics"""
        if not self.metrics['timestamps']:
            print("No metrics data available")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        timestamps = list(self.metrics['timestamps'])
        
        # Throughput
        ax1.plot(timestamps, list(self.metrics['throughput']))
        ax1.set_title('Throughput (Messages/sec)')
        ax1.set_ylabel('Messages/sec')
        ax1.tick_params(axis='x', rotation=45)
        
        # Latency
        ax2.plot(timestamps, list(self.metrics['latency']))
        ax2.set_title('Latency (ms)')
        ax2.set_ylabel('Latency (ms)')
        ax2.tick_params(axis='x', rotation=45)
        
        # CPU Usage
        ax3.plot(timestamps, list(self.metrics['cpu_usage']))
        ax3.set_title('CPU Usage (%)')
        ax3.set_ylabel('CPU %')
        ax3.tick_params(axis='x', rotation=45)
        
        # Memory Usage
        ax4.plot(timestamps, list(self.metrics['memory_usage']))
        ax4.set_title('Memory Usage (%)')
        ax4.set_ylabel('Memory %')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('automq_metrics.png')
        plt.show()
    
    def get_summary_stats(self):
        """Get summary statistics"""
        if not self.metrics['throughput']:
            return "No metrics available"
        
        return {
            'avg_throughput': sum(self.metrics['throughput']) / len(self.metrics['throughput']),
            'max_throughput': max(self.metrics['throughput']),
            'avg_latency': sum(self.metrics['latency']) / len(self.metrics['latency']),
            'max_latency': max(self.metrics['latency']),
            'avg_cpu': sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage']),
            'avg_memory': sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage'])
        }

# Performance testing script
def run_performance_test():
    """Run comprehensive performance test"""
    print("Starting AutoMQ Performance Test...")
    
    # Initialize monitor
    monitor = AutoMQMonitor()
    monitor.start_monitoring()
    
    try:
        # Import our producer and consumer
        from producer import EventProducer
        from consumer import EventConsumer
        
        # Test 1: Throughput test
        print("\n=== Throughput Test ===")
        producer = EventProducer()
        
        # Send 10000 messages
        start_time = time.time()
        producer.produce_batch(10000, delay=0)
        throughput_time = time.time() - start_time
        
        producer_stats = producer.get_stats()
        print(f"Producer Stats: {producer_stats}")
        producer.close()
        
        # Test 2: Consumer performance
        print("\n=== Consumer Test ===")
        consumer = EventConsumer(group_id='perf-test-group')
        
        # Consume messages
        start_time = time.time()
        consumer.consume_batch(max_messages=5000, timeout_ms=60000)
        consumer_time = time.time() - start_time
        
        consumer_stats = consumer.get_detailed_stats()
        print(f"Consumer Stats: {json.dumps(consumer_stats, indent=2)}")
        
        # Test 3: Concurrent producers
        print("\n=== Concurrent Producers Test ===")
        
        def producer_worker(worker_id, message_count):
            producer = EventProducer()
            producer.produce_batch(message_count, delay=0)
            stats = producer.get_stats()
            print(f"Producer {worker_id} stats: {stats}")
            producer.close()
        
        # Start multiple producers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=producer_worker, args=(i, 2000))
            threads.append(thread)
            thread.start()
        
        # Wait for all producers to complete
        for thread in threads:
            thread.join()
        
        # Wait a bit for metrics collection
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("Test interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")
    finally:
        monitor.stop_monitoring()
        
        # Generate report
        print("\n=== Final Performance Report ===")
        summary = monitor.get_summary_stats()
        print(json.dumps(summary, indent=2))
        
        # Plot metrics
        monitor.plot_metrics()

if __name__ == "__main__":
    run_performance_test()
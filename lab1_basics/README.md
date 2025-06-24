# AutoMQ Basic Producer & Consumer 

## What is AutoMQ?

AutoMQ is a Kafka-compatible, cloud-native messaging and streaming platform designed for high scalability, low latency, and cost efficiency. It leverages cloud infrastructure to provide a serverless Kafka alternative, maintaining compatibility with Kafka APIs while optimizing for cloud environments.

## Why Use AutoMQ?

AutoMQ is used to:
- Handle large-scale event streaming with minimal operational overhead.
- Provide a cost-effective alternative to traditional Apache Kafka deployments.
- Enable seamless integration with existing Kafka-based applications due to API compatibility.
- Support serverless scaling, reducing infrastructure management.

### Where is AutoMQ Used?

* **Streaming Data**: From IoT, logs, user events
* **Microservices**: For event-driven communication
* **Big Data**: Send data to tools like Spark/Flink
* **Messaging**: For apps like e-commerce, finance, gaming

### Pros of AutoMQ

* Works with **Kafka clients**
* **Auto-scales**, no manual config
* **Low cost** (pay-as-you-go)
* **Fast** (low latency, high throughput)
* Built for **cloud** use

### Cons of AutoMQ

* Needs **cloud setup** (not for offline use)
* Some **learning required**
* **Smaller ecosystem** than Kafka

## Diagram of Automq System:

![alt text](automq_diagram.svg)

This appears to be a system diagram for AutoMQ. Here, explanation of how AutoMQ works based on this diagram:

**1. Infrastructure**

* **Linux VM:** Runs Ubuntu 20.04+ with 4GB RAM, 2 CPU.
* **Docker Engine:** AutoMQ runs inside Docker containers.
* **Port 9092:** Open for Kafka-compatible communication.

---

**2. AutoMQ Broker (Core Engine)**

* Acts like a Kafka broker (v3.3.0-SNAPSHOT).
* Handles **message processing**, **storage**, and **topic management** (e.g., `test-topic`).
* Uses the **Kafka protocol** for compatibility with Kafka clients.
* Delivers messages to consumers.

---

**3. Kafka API Gateway**

* Exposes **Kafka-compatible APIs** on port 9092.
* Routes messages between clients and the AutoMQ Broker.
* Supports **produce** and **consume** operations.

---

**4. Client Applications**

* **Python Clients:** Use `kafka-python` to produce/consume messages.
* **Java Clients:** Use Kafka's standard client API.
* Both can connect to AutoMQ as if it's Kafka.

---

**5. Monitoring**

* Tracks **throughput**, **latency**, **system logs**, and **Docker logs**.
* Provides **debug info** and **audit trail** for troubleshooting and security.

## **How AutoMQ Works?**

![alt text](automq_workflow.svg)

1.  **Deployment:** AutoMQ components (Broker, API Gateway) are deployed as Docker containers on a Linux VM, leveraging the Docker Engine for runtime.
2.  **Client Connection:** Client applications (e.g., Python, Java) connect to the Kafka API Gateway over the network (Port 9092).
3.  **Producing Messages:**
    * A client application (Python Producer) uses a Kafka client library (e.g., `kafka-python`) to send messages.
    * These messages are sent to the Kafka API Gateway using Kafka-compatible APIs.
    * The Kafka API Gateway routes these messages to the AutoMQ Broker, which receives them via the Kafka Protocol.
    * The AutoMQ Broker processes these messages and stores them in relevant topics (e.g., "test-topic").
4.  **Consuming Messages:**
    * A client application (Python Consumer) uses a Kafka client API to request messages from the Kafka API Gateway.
    * The Kafka API Gateway, communicating with the AutoMQ Broker via the Kafka Protocol, retrieves the requested messages.
    * The AutoMQ Broker delivers the messages.
    * The Kafka API Gateway then sends these messages back to the client application.
5.  **Monitoring:** Throughout these operations, various logs (system, Docker), performance metrics (throughput, latency), and debugging information are collected to ensure the system's smooth operation and allow for troubleshooting.


## How to Use AutoMQ?

This lab guides you through deploying AutoMQ, writing a Python producer and consumer, and monitoring throughput/latency. Follow the steps below to set up and test AutoMQ on a cloud VM.

---

### Prerequisites

- **System Requirements**: Linux-based VM (Ubuntu 20.04+), 4GB RAM, 2 CPUs, 20GB disk.

- **Tools Needed**: Docker, Docker Compose, Python 3, Git, JDK 17.

- **Network**: Port 9092 open for Kafka communication.
  - *Why?* AutoMQ (Kafka-compatible) uses port 9092 for client communication, ensuring producers and consumers can connect to the broker.

---

## Deploying Kafka-Compatible Messaging with AutoMQ

### Step 1: Deploy AutoMQ

1. **Clone AutoMQ Repository**

   ```bash
   git clone https://github.com/AutoMQ/automq.git
   cd automq
   ```

   - Cloning the AutoMQ repository downloads the source code needed to build and deploy AutoMQ.

2. **Install JDK**

   ```bash
   sudo apt update
   sudo apt install openjdk-17-jdk -y
   java -version     #verifies the installation
   ```

   -  AutoMQ requires Java (JDK 17) to compile and run. Updating the package index ensures the latest JDK version is installed.

3. **Add Swap Temporarily**

   ```bash
   fallocate -l 2G /swapfile
   chmod 600 /swapfile
   mkswap /swapfile
   swapon /swapfile
   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
   export GRADLE_OPTS="-Xmx512m"
   ```

   - Swap space prevents memory exhaustion during the build process on low-RAM systems. Setting `JAVA_HOME` points to the JDK location, and `GRADLE_OPTS` limits Gradle’s memory usage to avoid crashes.

4. **Check memory**

   ```bash
   free -h
   df -h
   ```

   - These commands verify that swap space is active and sufficient, ensuring the system can handle the build without running out of memory.

5. **Build AutoMQ**

   ```bash
   ./gradlew releaseTarGz -x test -x check --no-daemon --info
   ```

   - This command uses Gradle to build AutoMQ and create a `.tgz` package, skipping tests and checks to speed up the process. The `--no-daemon` flag ensures a clean build, and `--info` provides detailed output for debugging.

   ## Expected Output:
    ![alt text](<automq build-1.png>)


6. **Copy `.tgz` to Docker Folder**

   ```bash
   cd core/build/distributions
   tar -xzf kafka-3.9.0-SNAPSHOT.tgz
   ls -l
   cd kafka-3.9.0-SNAPSHOT
   
   # Rename the file because the Dockerfile expects the archive to be named 'automq-3.9.0-SNAPSHOT.tgz'
   mv /root/code/Automq_basic/automq/core/build/distributions/kafka-3.9.0-SNAPSHOT.tgz /root/code/Automq_basic/automq/core/build/distributions/automq-3.9.0-SNAPSHOT.tgz  
  
   cp automq-3.9.0-SNAPSHOT.tgz /root/code/Automq_basic/automq/docker/
   ```

   - The build process creates a `.tgz` file, which needs to be extracted and moved to the Docker directory for image creation. Copying to the Docker folder prepares it for the next step.

   Core Folder Structure:

   ![alt text](<core folder ss-1.png>)

7. **Build Docker Image**

   ```bash
   cd docker
   docker build -t automqinc/automq:1.6.0 .
   ```

   - This command builds a custom Docker image for AutoMQ using the `.tgz` file, tagging it as `1.6.0`. The image encapsulates AutoMQ and its dependencies for consistent deployment.

8. **Run Docker Compose**

   ```bash
   docker-compose up -d
   ```

   - Docker Compose starts the AutoMQ container in detached mode (`-d`), setting up the broker and required services based on the `docker-compose.yml` configuration.

   ## Expected Output:

   ![alt text](<image build-1.png>)

9. **Check Broker Logs**

   ```bash
   docker-compose ps 
   docker logs automq-single-server | tail -n 50
   ```

   - Viewing the last 50 lines of logs confirms that the AutoMQ broker is running correctly and helps diagnose startup issues, such as misconfigurations or port conflicts.

---

## Producing and Consuming Events with AutoMQ Using Python Kafka-Compatible Clients

### Step 2: Set Up Python Environment

1. **Install Python Dependencies**

   ```bash
   apt update
   apt install -y python3-venv python3-pip
   ```

   - Python 3 and `pip` are needed to run the producer/consumer scripts, and `python3-venv` enables isolated environments. Updating the package index ensures the latest versions.

2. **Create Virtual Environment**

   ```bash
   cd automq/docker

   python3 -m venv /tmp/venv

   source /tmp/venv/bin/activate

   pip install --upgrade pip
   pip install kafka-python
   ```

   -  A virtual environment isolates Python dependencies, preventing conflicts. Activating it sets the context for installing `kafka-python`, the Kafka client library used for producer/consumer scripts. Upgrading `pip` ensures compatibility with the latest packages.

3. **Verify Broker Configuration**
     
   From this `config/broker.properties` file:
     
   Ensure:
   ```
   listeners=PLAINTEXT://:9092
   advertised.listeners=PLAINTEXT://localhost:9092
   ```

   - Verifying `listeners` and `advertised.listeners` ensures clients can connect to the broker on port 9092.

---

### Step 3: Create Producer and Consumer

1. **Access Container**

   ```bash
   docker exec -it automq-single-server bash
   ```

   - This command opens a shell inside the AutoMQ container, allowing you to create and run Python scripts in the same environment as the broker, avoiding network issues.

2. **Create Producer Script**

   ```bash
   cat > producer.py << 'EOF'
   from kafka import KafkaProducer
   import json
   import time

   producer = KafkaProducer(
       bootstrap_servers='localhost:9092',
       value_serializer=lambda v: json.dumps(v).encode('utf-8')
   )

   topic = 'test-topic'
   total_sent = 0
   start_time = time.time()

   for i in range(100):
       t0 = time.time()
       message = {'id': i, 'msg': f'Hello AutoMQ {i}', 'ts': t0}
       producer.send(topic, value=message)
       producer.flush()
       t1 = time.time()
       print(f"Sent msg {i} in {round((t1 - t0)*1000, 2)} ms")
       total_sent += 1

   end_time = time.time()
   duration = end_time - start_time
   print(f"\nSent {total_sent} messages in {round(duration, 2)} seconds")
   print(f"Throughput: {round(total_sent / duration, 2)} msg/sec")
   EOF
   ```

   - The producer script sends 100 JSON messages to the `test-topic`, measuring the time taken for each send and calculating throughput. Writing it directly with `cat` ensures accuracy and avoids manual editing errors.

3. **Create Consumer Script**

   ```bash
   cat > consumer.py << 'EOF'
   from kafka import KafkaConsumer
   import json
   import time

   consumer = KafkaConsumer(
       'test-topic',
       bootstrap_servers='localhost:9092',
       auto_offset_reset='latest',
       group_id='test1-monitor',
       value_deserializer=lambda m: json.loads(m.decode('utf-8'))
   )

   print("Listening...")

   total_received = 0
   latencies = []

   for message in consumer:
       receive_ts = time.time()
       sent_ts = message.value.get('ts', receive_ts)
       latency = receive_ts - sent_ts
       latencies.append(latency)
       total_received += 1

       print(f"Received msg {message.value['id']} with latency {round(latency*1000, 2)} ms")

       if total_received >= 100:
           break

   avg_latency = sum(latencies) / len(latencies)
   print(f"\nTotal received: {total_received}")
   print(f"Avg latency: {round(avg_latency * 1000, 2)} ms")
   EOF
   ```

   - The consumer script reads messages from `test-topic`, calculates latency for each message, and computes the average latency after receiving 100 messages. Using `cat` ensures the script is created correctly.

4. **Verify Scripts**

   ```bash
   cat producer.py
   cat consumer.py

   # edit
   nano producer.py
   nano consumer.py

   # overwrite
   cat > producer.py << 'EOF'
   new code....
   EOF
   cat > consumer.py << 'EOF'
   new code....
   EOF
   
   # delete file
   rm producer.py consumer.py

   ```

   -  Displaying the scripts confirms they were created correctly, allowing you to check for syntax errors or missing lines before running them.

---

### Step 4: Test Message Streaming

1. **Run Consumer**

   Open a terminal, activate the virtual environment, and start the consumer:

   ```bash
   docker exec -it automq-single-server bash
   source /tmp/venv/bin/activate
   python3 consumer.py
   ```

   - The consumer must run first to listen for messages on `test-topic`. 

2. **Run Producer**

   In another terminal, access the container, activate the virtual environment, and run the producer:

   ```bash
   docker exec -it automq-single-server bash
   source /tmp/venv/bin/activate
   python3 producer.py
   ```

   - The producer sends messages to the broker, which the consumer reads.

### OUTPUT:
   
   ![alt text](automq_api_test1-1.png)  
   
Running both inside the container ensures it uses the same environment as the broker, minimizing network issues.

   ![alt text](automq_api_test2-1.png)

3. **Monitor Output**
   - **Producer Output**: Displays the time taken to send each message and overall throughput (messages/second).
     -  This output helps evaluate the producer’s performance and AutoMQ’s ability to handle message sends.
   - **Consumer Output**: Shows the latency for each received message and the average latency.
     - Latency metrics indicate how quickly messages are delivered, reflecting AutoMQ’s efficiency.

---

 ## **Some Common Issues**

   - **Connection Errors**: Ensure `bootstrap_servers='localhost:9092'` and port 9092 is open.
     - Incorrect server addresses or closed ports prevent client-broker communication.
   - **Low Throughput**: Check system resources (CPU, memory, disk I/O).
     - Resource constraints can bottleneck message processing, indicating the need for a more powerful VM.

---

## Learning Outcomes

- **Kafka API Compatibility**: Understood how AutoMQ supports Kafka clients (`kafka-python`).
- **AutoMQ Basics**: Deployed AutoMQ, configured a broker, and ran producer/consumer scripts.
- **Performance Monitoring**: Measured throughput (messages/second) and latency (milliseconds).

---


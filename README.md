# AutoMQ Deployment Guide (With Docker + .tgz Build Fix)

## Deployment Instructions

### 1. Clone AutoMQ Repository

```bash
git clone https://github.com/AutoMQ/automq.git
cd automq
```
### 2. Install JDK

```bash
sudo apt update
sudo apt install openjdk-17-jdk -y
java -version
```

### 3. Add Swap Temporarily

This helps alleviate memory pressure during the build:

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export GRADLE_OPTS="-Xmx512m 
```

### 4. Confirm Swap:

```bash
free -h
df -h
```

### 5. Build .tgz Without Tests

```bash
./gradlew releaseTarGz -x test -x check --no-daemon --info

```


### 3. Copy `.tgz` to Docker Folder

```bash
cd core/build/distributions
tar -xzf kafka-3.9.0-SNAPSHOT.tgz
ls -l
cd kafka-3.9.0-SNAPSHOT
docker pull automqinc/automq:latest

mv /root/code/Automq_basic/automq/core/build/distributions/kafka-3.9.0-SNAPSHOT.tgz /root/code/Automq_basic/automq/core/build/distributions/automq-3.9.0-SNAPSHOT.tgz

cd ..

cp automq-3.9.0-SNAPSHOT.tgz /root/code/Automq_basic/automq/docker/

```

### 4. Build Docker Image

```bash
cd docker
docker build -t automqinc/automq:1.6.0 .

```

### 5. Run Docker Compose

```bash
docker-compose up -d
```

## Test Producer and Consumer:

pip install:

apt update
apt install -y python3-pip
pip install kafka-python

python3 producer.py
python3 consumer.py

## monitor latency from logs
docker logs -f automq-single-server | grep ElasticKafkaApis



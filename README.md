# AutoMQ Deployment Guide (With Docker + .tgz Build Fix)

## Deployment Instructions

### 1. Clone AutoMQ Repository

```bash
git clone https://github.com/AutoMQ/automq.git
cd automq/docker
```

### 2. Build Docker Image Locally

```bash
docker build -t automq-ce .
```
##### error:
```bash
Step 5/12 : COPY "./automq-*.tgz" /opt/kafka/kafka.tgz
COPY failed: no source files were specified
```

### 3. Update Docker Compose

Edit `docker-compose.yml` file:

```yaml
image: automq-ce
```

### 4. Run Docker Compose

```bash
docker-compose up -d
```

---

# .tgz Build Issue Fixation

If you encounter `.tgz` build errors or out-of-memory issues, follow these steps:

### 1. Clone Repo and Install JDK

```bash
git clone https://github.com/AutoMQ/automq.git
cd automq

sudo apt update
sudo apt install openjdk-17-jdk -y
java -version
```

### 2. Build .tgz Without Tests

```bash
./gradlew releaseTarGz -x test -x check --no-daemon --info

```

### 3. Copy `.tgz` to Docker Folder

```bash
cd /root/code/Automq_basic/automq/core/build/distributions/
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

---

## Recommended Gradle Fix for Low-Memory Systems


##  Add Swap Temporarily

This helps alleviate memory pressure during the build:

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Confirm Swap:

```bash
free -h
```


Run Gradle with aggressively reduced memory usage:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export GRADLE_OPTS="-Xmx512m -XX:MaxMetaspaceSize=128m -Dorg.gradle.jvmargs='-Xmx512m'"

./gradlew releaseTarGz -x test -x check --no-daemon --no-parallel --stacktrace
```


## extra note:
pip install:

apt update
apt install -y python3-pip


> **No space left on device**

### 1. Check Disk Space

```bash
df -h
```

###  2. Clean Up Unnecessary Files

#### A. Clean up Docker system 

```bash
docker system prune -af
```

#### B. Clean apt cache

```bash
apt clean
```

#### C. Delete old log files

```bash
rm -rf /var/log/*.gz /var/log/*.1 /var/log/journal/*
```

#### D. Clear Gradle cache (if you're low on space)

```bash
rm -rf ~/.gradle/caches/
```

#### E. Delete temporary `.zip` or `.tgz` files

```bash
find / -type f \( -name "*.zip" -o -name "*.tgz" \) -delete 2>/dev/null
```


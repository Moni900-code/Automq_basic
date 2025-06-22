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

## .tgz Build Issue Fixation

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
./gradlew releaseTarGz -x test -x check
```

### 3. Copy `.tgz` to Docker Folder

```bash
cp build/distributions/automq-*.tgz docker/
```

### 4. Build Docker Image

```bash
cd docker
docker build -t automq-ce .
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



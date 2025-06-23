FROM openjdk:17-slim

WORKDIR /app

COPY ./automq-*.tgz ./automq.tgz

RUN mkdir -p /opt/kafka && \
    tar -xzf automq.tgz -C /opt/kafka --strip-components=1 && \
    rm automq.tgz

ENV PATH=\"$PATH:/opt/kafka/bin\"

EXPOSE 9092 8080

CMD [\"kafka-server-start.sh\", \"/opt/kafka/config/server.properties\"]

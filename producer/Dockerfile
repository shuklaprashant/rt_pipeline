FROM python:3.9-alpine

# Set working directory
WORKDIR /app

# Install build dependencies required for compiling librdkafka and Python packages
RUN apk add --no-cache --virtual .build-deps gcc g++ musl-dev bash make wget git && \
    apk add --no-cache musl-dev zlib-dev openssl zstd-dev pkgconfig libc-dev python3-dev && \
    wget -O librdkafka-2.13.0.tar.gz https://github.com/confluentinc/librdkafka/archive/refs/tags/v2.13.0.tar.gz && \
    tar -xzf librdkafka-2.13.0.tar.gz && cd librdkafka-2.13.0 && ./configure --prefix /usr && make && make install && \
    cd /app && rm -rf librdkafka-2.13.0 librdkafka-2.13.0.tar.gz && \
    apk add --no-cache netcat-openbsd && \
    apk del .build-deps

# Install Python dependencies after librdkafka is available
COPY requirements.txt /app/requirements.txt
RUN apk add --no-cache --virtual .build-deps gcc g++ musl-dev python3-dev && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apk del .build-deps

# Copy the necessary files from the local machine
COPY schema /app/schema
COPY src/producer.py /app/src/producer.py

# Set environment variables for the Python script
ENV KAFKA_BOOTSTRAP_SERVER=kafka-broker-1:9092
ENV KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081
ENV SCHEMA_FILE_LOCATION=/app/schema/pageviews.avsc
ENV PRODUCER_MAX_SLEEP_TIME_SECONDS=2

# Wait for Kafka to start and then run the Python script
CMD ["sh", "-c", "while ! nc -z kafka-broker-1 9092 || ! nc -z schema-registry 8081; do sleep 1; done; python src/producer.py"]

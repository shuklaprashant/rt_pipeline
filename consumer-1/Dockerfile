FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev librdkafka-dev netcat-openbsd

RUN apk add --no-cache --virtual .build-deps gcc g++ musl-dev bash make wget git && \
    apk add --no-cache musl-dev zlib-dev openssl zstd-dev pkgconfig libc-dev python3-dev && \
    wget -O librdkafka-2.13.0.tar.gz https://github.com/confluentinc/librdkafka/archive/refs/tags/v2.13.0.tar.gz && \
    tar -xzf librdkafka-2.13.0.tar.gz && cd librdkafka-2.13.0 && ./configure --prefix /usr && make && make install && \
    cd /app && rm -rf librdkafka-2.13.0 librdkafka-2.13.0.tar.gz && \
    apk add --no-cache netcat-openbsd && \
    apk del .build-deps

COPY src/consumer-1.py /app/src/consumer-1.py

ENV KAFKA_BOOTSTRAP_SERVER=kafka-broker-1:9092
ENV KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "src/consumer-1.py"]


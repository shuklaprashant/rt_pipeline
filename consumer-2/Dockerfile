FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev librdkafka-dev netcat-openbsd

RUN apk add --no-cache --virtual .make-deps bash make wget git gcc g++ && apk add --no-cache musl-dev zlib-dev openssl zstd-dev pkgconfig libc-dev
RUN wget https://github.com/edenhill/librdkafka/archive/v2.5.3.tar.gz
RUN tar -xvf v2.5.3.tar.gz && cd librdkafka-2.5.3 && ./configure --prefix /usr && make && make install

COPY src/consumer-2.py /app/src/consumer-2.py

ENV KAFKA_BOOTSTRAP_SERVER=kafka-broker-1:9092
ENV KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "src/consumer-2.py"]


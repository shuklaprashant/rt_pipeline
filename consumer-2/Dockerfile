FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev librdkafka-dev netcat-openbsd

COPY src/consumer-2.py /app/src/consumer-2.py

ENV KAFKA_BOOTSTRAP_SERVER=kafka-broker-1:9092
ENV KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["sh", "-c", "while ! nc -z mongodb 27017; do sleep 1; done; sleep 40; python src/consumer-2.py"]

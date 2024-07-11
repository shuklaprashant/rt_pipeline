FROM python:3.9-alpine

# Set working directory
WORKDIR /app

RUN apk add --no-cache gcc musl-dev librdkafka-dev netcat-openbsd

RUN apk add --no-cache --virtual .make-deps bash make wget git gcc g++ && apk add --no-cache musl-dev zlib-dev openssl zstd-dev pkgconfig libc-dev
RUN wget https://github.com/edenhill/librdkafka/archive/v2.5.0.tar.gz
RUN tar -xvf v2.5.0.tar.gz && cd librdkafka-2.5.0 && ./configure --prefix /usr && make && make install

# Copy the necessary files from the local machine
COPY data /app/data
COPY schema /app/schema
COPY src/producer.py /app/src/producer.py

# Set environment variables for the Python script
ENV KAFKA_BOOTSTRAP_SERVER=kafka-broker-1:9092
ENV KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081
ENV CSV_FILE_LOCATION=/app/data/LFB_Incident_data_from_January_2017.csv.gz
ENV SCHEMA_FILE_LOCATION=/app/schema/incident_schema.avsc
ENV PRODUCER_MAX_SLEEP_TIME_SECONDS = 5

# Install required Python packages (assuming you have a requirements.txt)
# If you don't, you can directly install packages using RUN pip install <package_name>
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Wait for Kafka to start and then run the Python script
CMD ["sh", "-c", "while ! nc -z kafka-broker-1 9092 || ! nc -z schema-registry 8081; do sleep 1; done; python src/producer.py"]

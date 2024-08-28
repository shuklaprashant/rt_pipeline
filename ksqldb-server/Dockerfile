# Stage 1: Download JMX Exporter
FROM alpine:latest AS downloader

# Install curl in the alpine image
RUN apk --no-cache add curl

# Download the JMX Exporter JAR file
RUN curl -L -o /jmx_prometheus_javaagent.jar \
    https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.16.1/jmx_prometheus_javaagent-0.16.1.jar

# Stage 2: Build the ksqlDB server image with JMX Exporter
FROM confluentinc/cp-ksqldb-server:7.6.1

# Copy JMX Exporter JAR from the downloader stage
COPY --from=downloader /jmx_prometheus_javaagent.jar /opt/jmx_prometheus_javaagent.jar

# Copy the JMX Exporter configuration file
COPY config.yaml /opt/config.yaml

# Set the KSQL_OPTS environment variable to include the JMX Exporter
ENV KSQL_OPTS="-javaagent:/opt/jmx_prometheus_javaagent.jar=7072:/opt/config.yaml"

# Expose necessary ports
EXPOSE 8088 1099 7072

# Start the ksqlDB server
CMD ["/etc/confluent/docker/run"]

FROM confluentinc/cp-ksqldb-cli:latest

COPY scripts /scripts

ENV TOPIC_NAME='incident'

ENTRYPOINT ["/scripts/wait-for-ksql-server.sh"]

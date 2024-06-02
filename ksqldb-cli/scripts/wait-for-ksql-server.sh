#!/bin/bash
set -e

KSQL_SERVER_URL="http://ksqldb-server:8088"

function check_ksql_server() {
  curl -s "$KSQL_SERVER_URL/info" | grep -q 'ksqlServiceId'
}

echo "Waiting for ksqlDB server to be ready..."
until check_ksql_server; do
  echo "ksqlDB server is not ready yet. Retrying in 5 seconds..."
  sleep 5
done

sleep 30

echo "ksqlDB server is ready. Executing the SQL script..."
ksql "http://ksqldb-server:8088" --file /scripts/stream_table.sql

tail -f /dev/null

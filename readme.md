Pre-requisite-
    - Docker compose is installed.
    - AWS ACCESS KEY and SECRET KEY
    - S3 Bucket to store raw data and aggregated data.
    - Local computer had sufficient RAM and storage, available to Docker
    - Internet

Set-up:
    - Clone the repo.
    - Make sure terminal is pointing to -> rt-pipeline.
    - Update docker-compose file with AWS Access Key, Secret Key, AWS Region and S3 buckets for both raw and aggrgated data.
    - Optional: Use Env variable- "TOTAL_EVENTS_TO_GENERATE" to set the number of events to generate. Set to 10000.

How to run the project:
Steps:
    1. `docker compose up --build -d`
    2. Wait for a few moments, let the Container start. Verify the running status- `docker compose logs consumer-1` and `docker compose logs consumer-2`

How to Query the results:
Steps:
    1. Login to your AWS S3 and verify the buckets. raw and aggregated data should be stored as json in respective buckets.


Required version I have used to develop and test:
1. macOS Sonoma 14.5
2. Docker Desktop version- 4.31.0 // Compose: v2.27.1-desktop.1
3. Python 3.11.5
4. Docker Base Images (All latest- Kafka, Ksql, Python3.9-Alpine)

Monitoring:
    1. Go to Grafana > http://localhost:3000
    2. Add source > Prometheus
    3. Dashboard > New > Import > Sample Grafana Dashboard 
        - Select node_exporter_full.json
    4. Verify the metrics like CPU/Memory/Storage Utilisation.
    
### Prerequisites
- **Docker Compose** is installed.
- **AWS Access Key** and **Secret Key**.
- An **S3 Bucket** for storing raw and aggregated data.
- **Sufficient RAM and Storage** on your local computer, available to Docker.
- **Internet Connectivity**.

### Setup Instructions
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/shuklaprashant/rt_pipeline.git
    ```
2. **Navigate to the Project Directory**:
    ```bash
    cd rt-pipeline
    ```
3. **Update the Docker Compose Configuration**:
    - Modify the `docker-compose.yml` file:
        - Enter your **AWS Access Key**, **Secret Key**, **AWS Region**, and the **S3 Buckets** for both raw and aggregated data.
4. **Optional Configuration**:
    - Set the environment variable `TOTAL_EVENTS_TO_GENERATE` to specify the number of events to generate (default is set to `10000`)

### How to Run the Project
1. **Start the Containers**:
    ```bash
    docker compose up --build -d
    ```
2. **Verify the Container Status**:
    - Wait for the containers to start, then check their logs:
    ```bash
    docker compose logs consumer-1
    docker compose logs consumer-2
    ```

### How to Query the Results
1. **Check S3 Buckets**:
    - Log in to your AWS S3 console.
    - Verify that the raw and aggregated data are stored as JSON files in the respective buckets.

### Development and Testing Environment
- **Operating System**: macOS Sonoma 14.5
- **Docker Desktop Version**: 4.31.0 (Compose: v2.27.1-desktop.1)
- **Python Version**: 3.11.5
- **Docker Base Images**: Latest versions for Kafka, KSQL, Python 3.9-Alpine

### Monitoring the System
1. **Access Grafana**:
    - Open Grafana in your browser at: [http://localhost:3000](http://localhost:3000)
2. **Add a Data Source**:
    - Go to `Configuration` > `Data Sources`.
    - Add **Prometheus** as the data source.
3. **Import a Sample Dashboard**:
    - Go to `Dashboard` > `New` > `Import`.
    - Select `node_exporter_full.json` to import a sample Grafana dashboard.
4. **Monitor Metrics**:
    - Verify metrics like CPU, Memory, and Storage Utilization for ksqldb-server.

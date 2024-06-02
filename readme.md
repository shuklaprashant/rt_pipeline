Pre-requisite-
    - Docker compose is installed.
    - Local computer had sufficient RAM and storage, available to Docker
    - Basic knowledge of MongoDB and java-script- to help modifying the queries to see desired results.

Set-up:
    - Copy the folder.
    - Make sure terminal is pointing to -> ds-lfb-project.

How to run the project:
Steps:
    1. `docker compose up --build -d`
    2. Wait for 2-4 minutes, let the Container start consuming the data and MongoDB is ready to serve. You can verify by running- `docker compose logs consumer-2`

How to Query the results:
Steps:
    1. `docker cp example-queries mongo:example-queries`
    2. Execute query
        `docker exec -it mongo mongosh --file example-queries/GLOBAL_RESPONSE_TIME_vs_30DAYS.js`
    3. For Day/Month/Year aggregation, please modify- `DATEOFCALL: { $regex: ".*2017" }` and
       copy the scripts file to Mongo container (use step-3) and run the script (use step 4).


Required version I have used to develop and test:
1. macOS Monterey 12.7.5
2. Docker version- Docker version 26.1.1
3. Python 3.11.5
4. Docker Base Images (All latest- Kafka, Mongo, Python3.9-Alpine)




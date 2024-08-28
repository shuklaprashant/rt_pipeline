CREATE STREAM PAGEVIEWS (
        USER_ID INT, 
        POSTCODE STRING, 
        WEBPAGE STRING, 
        AT_TIME TIMESTAMP
        ) 
        WITH (
            KAFKA_TOPIC='page_views', 
            KEY_FORMAT='KAFKA', 
            VALUE_FORMAT='AVRO'
            );

CREATE TABLE PAGE_VIEWS_COUNT 
WITH (
    KAFKA_TOPIC='PAGE_VIEWS_COUNT', 
    KEY_FORMAT='AVRO', 
    PARTITIONS=1, 
    REPLICAS=1) AS 
    SELECT 
        POSTCODE AS POSTCODE,
        STRUCT(
            "POSTCODE":= AS_VALUE("POSTCODE"), 
            "TOTAL_VIEWS":= COUNT(*),
            "START_AT":= WINDOWSTART,
            "END_AT":= WINDOWEND
        ) as data
    FROM "PAGEVIEWS"
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY POSTCODE
EMIT FINAL;
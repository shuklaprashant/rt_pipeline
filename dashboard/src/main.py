import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Kafka configurations
KAFKA_BOOTSTRAP_SERVER = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "kafka-broker-1:9092")
KAFKA_SCHEMA_REGISTRY_URL = os.environ.get("KAFKA_SCHEMA_REGISTRY_URL", "http://schema-registry:8081")

# Message queues for thread-safe communication
pageview_queue = queue.Queue()
count_queue = queue.Queue()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.active_count_connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, connection_type: str):
        await websocket.accept()
        if connection_type == "pageviews":
            self.active_connections.add(websocket)
        elif connection_type == "count":
            self.active_count_connections.add(websocket)

    def disconnect(self, websocket: WebSocket, connection_type: str):
        if connection_type == "pageviews":
            self.active_connections.discard(websocket)
        elif connection_type == "count":
            self.active_count_connections.discard(websocket)

    async def broadcast(self, message: dict, connection_type: str):
        connections = self.active_connections if connection_type == "pageviews" else self.active_count_connections
        disconnected = set()
        if connections:
            logger.info(f"[BROADCAST] Broadcasting {connection_type} message to {len(connections)} clients: {message}")
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
        
        for conn in disconnected:
            self.disconnect(conn, connection_type)

manager = ConnectionManager()

# Data holders
current_stats = {
    "total_events": 0,
    "pageviews_by_postcode": {},
    "top_webpages": {},
}

counts_by_postcode = {}

def consume_pageviews():
    """Consume pageviews from Kafka"""
    logger.info("[PAGEVIEWS] Starting consumer thread")
    
    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
        'group.id': f'dashboard-pageviews-{int(datetime.now().timestamp())}',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'session.timeout.ms': 60000,
    }
    
    logger.info(f"[PAGEVIEWS] Consumer config: {consumer_conf}")
    
    try:
        consumer = Consumer(consumer_conf)
        logger.info("[PAGEVIEWS] Consumer created")
        consumer.subscribe(['page_views'])
        logger.info("[PAGEVIEWS] Subscribed to page_views topic")
        
        schema_registry_client = SchemaRegistryClient({'url': KAFKA_SCHEMA_REGISTRY_URL})
        avro_deserializer = AvroDeserializer(schema_registry_client)
        logger.info("[PAGEVIEWS] Avro deserializer created")
        
        logger.info("Started consuming pageviews from page_views topic")
        message_count = 0
        
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"[PAGEVIEWS] Consumer error: {msg.error()}")
                    break
            
            try:
                # Deserialize the message
                if msg.value():
                    value = avro_deserializer(msg.value(), None)
                    message_count += 1
                    
                    # Log raw value for debugging
                    logger.info(f"[PAGEVIEWS] Message {message_count}: {value}")
                    
                    current_stats["total_events"] += 1
                    
                    postcode = value.get('postcode', 'Unknown')
                    webpage = value.get('webpage', 'Unknown')
                    user_id = value.get('user_id', 'Unknown')
                    
                    # Update stats
                    if postcode not in current_stats["pageviews_by_postcode"]:
                        current_stats["pageviews_by_postcode"][postcode] = 0
                    current_stats["pageviews_by_postcode"][postcode] += 1
                    
                    if webpage not in current_stats["top_webpages"]:
                        current_stats["top_webpages"][webpage] = 0
                    current_stats["top_webpages"][webpage] += 1
                    
                    # Put message in queue for async broadcasting
                    pageview_queue.put({
                        "type": "pageview",
                        "data": {
                            "user_id": user_id,
                            "postcode": postcode,
                            "webpage": webpage,
                            "timestamp": datetime.now().isoformat()
                        },
                        "stats": current_stats.copy()
                    })
                    
            except Exception as e:
                logger.error(f"[PAGEVIEWS] Error processing: {e}", exc_info=True)
    
    except Exception as e:
        logger.error(f"[PAGEVIEWS] Consumer error: {e}", exc_info=True)
    finally:
        logger.info("[PAGEVIEWS] Closing consumer")
        consumer.close()

def consume_page_counts():
    """Consume PAGE_VIEWS_COUNT from Kafka"""
    logger.info("[COUNTS] Starting consumer thread")
    
    consumer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
        'group.id': f'dashboard-counts-{int(datetime.now().timestamp())}',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'session.timeout.ms': 60000,
    }
    
    logger.info(f"[COUNTS] Consumer config: {consumer_conf}")
    
    try:
        consumer = Consumer(consumer_conf)
        logger.info("[COUNTS] Consumer created")
        consumer.subscribe(['PAGE_VIEWS_COUNT'])
        logger.info("[COUNTS] Subscribed to PAGE_VIEWS_COUNT topic")
        
        schema_registry_client = SchemaRegistryClient({'url': KAFKA_SCHEMA_REGISTRY_URL})
        avro_deserializer = AvroDeserializer(schema_registry_client)
        logger.info("[COUNTS] Avro deserializer created")
        
        logger.info("Started consuming PAGE_VIEWS_COUNT from PAGE_VIEWS_COUNT topic")
        message_count = 0
        
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"[COUNTS] Consumer error: {msg.error()}")
                    break
            
            try:
                if msg.value():
                    value = avro_deserializer(msg.value(), None)
                    key = avro_deserializer(msg.key(), None) if msg.key() else None
                    message_count += 1
                    
                    # Log raw value for debugging
                    logger.info(f"[COUNTS] Message {message_count}: key={key}, value={value}")
                    
                    postcode = key if key else value.get('POSTCODE', 'Unknown')
                    
                    # Handle both nested 'DATA' field and direct fields
                    data_obj = value.get('DATA', value)
                    if isinstance(data_obj, dict):
                        total_views = data_obj.get('TOTAL_VIEWS', 0)
                        start_at = data_obj.get('START_AT', '')
                        end_at = data_obj.get('END_AT', '')
                    else:
                        total_views = value.get('TOTAL_VIEWS', 0)
                        start_at = value.get('START_AT', '')
                        end_at = value.get('END_AT', '')
                    
                    counts_by_postcode[postcode] = {
                        "total_views": total_views,
                        "start_at": start_at,
                        "end_at": end_at
                    }
                    
                    # Put message in queue for async broadcasting
                    count_queue.put({
                        "type": "count_update",
                        "data": {
                            "postcode": postcode,
                            "total_views": total_views,
                            "start_at": start_at,
                            "end_at": end_at,
                            "timestamp": datetime.now().isoformat()
                        },
                        "all_counts": counts_by_postcode.copy()
                    })
                    
            except Exception as e:
                logger.error(f"[COUNTS] Error processing: {e}", exc_info=True)
    
    except Exception as e:
        logger.error(f"[COUNTS] Consumer error: {e}", exc_info=True)
    finally:
        logger.info("[COUNTS] Closing consumer")
        consumer.close()

# Global reference to the message processor task
message_processor_task = None

# Async function to process queued messages
async def process_message_queues():
    """Process messages from queues and broadcast to WebSocket clients"""
    logger.info("[PROCESSOR] Starting message queue processor...")
    message_count = 0
    while True:
        try:
            # Process pageview queue
            while not pageview_queue.empty():
                try:
                    message = pageview_queue.get_nowait()
                    message_count += 1
                    if message_count <= 10:
                        logger.info(f"[PROCESSOR] Broadcasting pageview message to {len(manager.active_connections)} clients")
                    await manager.broadcast(message, "pageviews")
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"[PROCESSOR] Error processing pageview queue: {e}")
            
            # Process count queue
            while not count_queue.empty():
                try:
                    message = count_queue.get_nowait()
                    logger.info(f"[PROCESSOR] Broadcasting count message to {len(manager.active_count_connections)} clients")
                    await manager.broadcast(message, "count")
                except queue.Empty:
                    break
                except Exception as e:
                    logger.error(f"[PROCESSOR] Error processing count queue: {e}")
            
            # Small delay to prevent busy loop
            await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"[PROCESSOR] Unexpected error: {e}", exc_info=True)
            await asyncio.sleep(1)

# Start consumer threads
@app.on_event("startup")
async def startup_event():
    global message_processor_task
    logger.info("Starting Kafka consumers and message processor...")
    
    # Start pageviews consumer in a separate thread
    logger.info("Creating pageviews consumer thread...")
    pageviews_thread = threading.Thread(target=consume_pageviews, daemon=True)
    pageviews_thread.start()
    logger.info("Pageviews consumer thread started")
    
    # Start counts consumer in a separate thread
    logger.info("Creating counts consumer thread...")
    counts_thread = threading.Thread(target=consume_page_counts, daemon=True)
    counts_thread.start()
    logger.info("Counts consumer thread started")
    
    # Start the async message processor
    logger.info("Starting async message processor...")
    message_processor_task = asyncio.create_task(process_message_queues())
    logger.info("Async message processor task created")

@app.get("/")
async def get():
    return FileResponse("index.html", media_type="text/html")

@app.get("/api/stats")
async def get_stats():
    return {
        "stats": current_stats,
        "counts": counts_by_postcode
    }

@app.websocket("/ws/pageviews")
async def websocket_pageviews_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "pageviews")
    try:
        # Send current stats on connection
        await websocket.send_json({
            "type": "initial",
            "stats": current_stats
        })
        logger.info("Sent initial stats to pageviews client")
        while True:
            # Wait for client messages (ping, pong, etc.)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                if data:
                    logger.debug(f"Received from pageviews client: {data}")
            except asyncio.TimeoutError:
                # Send a ping to keep connection alive
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, "pageviews")
        logger.info("Pageviews client disconnected")
    except Exception as e:
        logger.error(f"Error in pageviews websocket: {e}")
        manager.disconnect(websocket, "pageviews")

@app.websocket("/ws/counts")
async def websocket_counts_endpoint(websocket: WebSocket):
    await manager.connect(websocket, "count")
    try:
        # Send current counts on connection
        await websocket.send_json({
            "type": "initial",
            "counts": counts_by_postcode
        })
        logger.info("Sent initial counts to client")
        while True:
            # Wait for client messages (ping, pong, etc.)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                if data:
                    logger.debug(f"Received from counts client: {data}")
            except asyncio.TimeoutError:
                # Send a ping to keep connection alive
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, "count")
        logger.info("Counts client disconnected")
    except Exception as e:
        logger.error(f"Error in counts websocket: {e}")
        manager.disconnect(websocket, "count")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
This module provides an implementation of a WebSocket server that simulates the live generation
of Web Page Visits Event.

The WebSocket is running on port 5678.
"""

import asyncio
import json
import os
import random
import logging
import websockets
import generate_page_view

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PRODUCER_MAX_SLEEP_TIME_SECONDS = int(os.environ.get("PRODUCER_MAX_SLEEP_TIME_SECONDS", 5))
TOTAL_EVENTS_TO_GENERATE = int(os.environ.get("TOTAL_EVENTS_TO_GENERATE", 1000))

def print_log(websocket, data):
    srv_host = websocket.host
    srv_port = websocket.port
    destination_host = websocket.remote_address[0]
    destination_port = websocket.remote_address[1]
    log_message = f"[{srv_host}:{srv_port} -> {destination_host}:{destination_port}] {data.decode('utf-8')}"
    logger.info(log_message)

async def rt_simulator(websocket, _):
    try:
        logger.info("Starting real-time simulator with {} events to generate.".format(TOTAL_EVENTS_TO_GENERATE))
        dict_stream = generate_page_view.generate_page_view_event(TOTAL_EVENTS_TO_GENERATE)
        for row in dict_stream:
            data = json.dumps(row, ensure_ascii=False).encode("utf8")
            await websocket.send(data)
            print_log(websocket, data)
            # Simulate a wait time before sending the next row
            await asyncio.sleep(random.randint(0, PRODUCER_MAX_SLEEP_TIME_SECONDS))
        logger.info("Completed sending all events.")
    except Exception as e:
        logger.error(f"Error in rt_simulator: {e}")

async def hello(websocket, _):
    try:
        data = "HELLO"
        await websocket.send(data.encode('utf-8'))
        print_log(websocket, data.encode('utf-8'))
    except Exception as e:
        logger.error(f"Error in hello function: {e}")

if __name__ == "__main__":
    try:
        logger.info("Starting WebSocket servers on ports 5678 (event data) and 5679 (health check).")
        event_data_server = websockets.serve(rt_simulator, "0.0.0.0", 5678)
        health_check_server = websockets.serve(hello, "0.0.0.0", 5679)

        asyncio.get_event_loop().run_until_complete(asyncio.gather(event_data_server, health_check_server))
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        logger.error(f"Error in main: {e}")
    except KeyboardInterrupt:
        logger.info("WebSocket servers stopped.")

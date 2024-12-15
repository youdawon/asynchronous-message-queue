from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import json

from src.service_b.message_subscriber import MessageSubscriber
from src.websocket.websocket_handler import WebSocketHandler
from src.utils.logger import logger
from src.utils.config import WEBSOCKET_POLL_INTERVAL_SECONDS, WEBSOCKET_MAX_RETRIES, WEBSOCKET_RETRY_DELAY_SECONDS

message_subscriber = MessageSubscriber()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await message_subscriber.connect():
        logger.info("[serviceB:Lifespan] Failed to connect to message subscriber.")        
        raise RuntimeError("serviceB")

    logger.info("[serviceB:Lifespan] Message subscriber connected.")

    yield

    logger.info("[serviceB:Lifespan] Shutting down...")
    if await message_subscriber.disconnect():
        logger.info("[serviceB:Lifespan] Message subscriber disconnected.")

app = FastAPI(lifespan=lifespan)

app.mount("/client", StaticFiles(directory="src/client", html=True), name="client")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    web_socket_handler = WebSocketHandler(websocket)
    await web_socket_handler.accept_connection()
    logger.info("[websocket_endpoint] WebSocket connected.")

    while True:
        # This loop implements a polling mechanism to check for new messages in the Redis queue.
        # A delay is applied between each iteration using WEBSOCKET_POLL_INTERVAL_SECONDS.        
        try:
            serialized_message = await message_subscriber.subscribe()
            if serialized_message:
                await web_socket_handler.send_message(serialized_message)

            await asyncio.sleep(WEBSOCKET_POLL_INTERVAL_SECONDS)

        except Exception as e:
            logger.warning("[websocket_endpoint] Error: %s", e)
            reconnected = await handle_reconnection(web_socket_handler)
            if not reconnected:
                await web_socket_handler.close_connection()
                return


async def handle_reconnection(web_socket_handler):
    for attempt in range(WEBSOCKET_MAX_RETRIES):
        try:
            logger.info("[serviceB:handle_reconnection] Reconnecting (Attempt %s/%s", attempt + 1, WEBSOCKET_MAX_RETRIES, ")")
            await web_socket_handler.accept_connection()
            logger.info("[serviceB:handle_reconnection] Reconnected successfully.")
            return True
        except Exception as reconnect_error:
            logger.error("[serviceB:handle_reconnection] Reconnection failed: %s", reconnect_error)
            await asyncio.sleep(WEBSOCKET_RETRY_DELAY_SECONDS)

    logger.error("[serviceB:handle_reconnection] Max retries reached. Closing WebSocket.")
    return False
        
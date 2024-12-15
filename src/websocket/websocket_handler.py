import json
import traceback
import asyncio
from fastapi import WebSocket
from starlette.websockets import WebSocketState

from src.utils.logger import logger
from src.utils.config import WEBSOCKET_MAX_RETRIES, REDIS_RETRY_DELAY_SECONDS, WEBSOCKET_RETRY_DELAY_SECONDS

class WebSocketHandler:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        if self.websocket.client_state != WebSocketState.CONNECTED:
            logger.warning("[WebSocketHandler:init] WebSocket is not in a connected state.")


    async def accept_connection(self):
        try:
            await self.websocket.accept()
            logger.info("[WebSocketHandler:accept_connection] WebSocket connection established.")
        except Exception as e:
            logger.error("[WebSocketHandler:accept_connection] Failed to accept connection: %s", e)
            traceback.print_exc()
            raise


    async def send_message(self, message, max_retries=WEBSOCKET_MAX_RETRIES, retry_delay=REDIS_RETRY_DELAY_SECONDS):
        try:
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_text(json.dumps(message))
                logger.info("[WebSocketHandler:send_message] Message sent: %s", message)
            else:
                raise RuntimeError("WebSocket is not connected.")
        except Exception as e:
            logger.error("[WebSocketHandler:send_message] Error sending message: %s", e)
            raise


    async def close_connection(self):
        try:
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.close()
                logger.info("[WebSocketHandler:close_connection] WebSocket connection closed.")
            else:
                logger.warning("[WebSocketHandler:close_connection] WebSocket is already closed.")
        except Exception as e:
            logger.error("[WebSocketHandler:close_connection] Failed to close connection: %s", e)
            traceback.print_exc()

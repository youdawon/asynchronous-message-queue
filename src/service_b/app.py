from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import json

from src.service_b.message_subscriber import MessageSubscriber
from src.utils.logger import logger
from src.utils.config import WEBSOCKET_POLL_INTERVAL_SECONDS

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


app.mount("/static", StaticFiles(directory="src/service_b/static", html=True), name="static")


@app.get('/message')
async def consume_message():
    response = await message_subscriber.subscribe()

    if not response:
        logger.info("[app:consume_message] The queue is empty")
        return {"status": "empty", "message": "The queue is empty"}
    
    return {"status": "success", "message": response}


@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()
    logger.info("[serviceB:websocket_endpoint] websocket is connected")
    try:
        while True:
            serialized_message = await message_subscriber.subscribe()
            if serialized_message:
                logger.info("[serviceB:websocket_endpoint] response : %s", serialized_message)            
                await websocket.send_text(json.dumps(serialized_message))

            logger.debug("[serviceB:websocket_endpoint] sleep %s seconds", WEBSOCKET_POLL_INTERVAL_SECONDS)                 
            await asyncio.sleep(WEBSOCKET_POLL_INTERVAL_SECONDS)
    except Exception as e:
        logger.error("[serviceB:websocket_endpoint] Exception : %s", e)            
    finally:
        await websocket.close()
        logger.info("[serviceB:websocket_endpoint] websocket is closed")        
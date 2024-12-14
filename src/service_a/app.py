from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
import json

from src.service_a.message import Message
from src.service_a.message_publisher import MessagePublisher
from src.utils.config import MESSAGE_MAX_CONTENT_LENGTH
from src.utils.logger import logger

message_publisher = MessagePublisher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if await message_publisher.connect():
        logger.info("[serviceA:Lifespan] Message publisher connected")
    else:
        logger.error("[serviceA:Lifespan] Failed to connect to message publisher")        
        raise RuntimeError()

    yield

    logger.info("[serviceA:Lifespan] Shutting down")
    if await message_publisher.disconnect():
        logger.info("[serviceA:Lifespan] Message publisher disconnected")


app = FastAPI(lifespan=lifespan)

@app.post('/message')
async def produce_message(message:Message):

    if not message.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="message is empty")
    
    if len(message.content) > MESSAGE_MAX_CONTENT_LENGTH:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="message is too long")
    
    message_data_dict = message.model_dump()

    serialized_message = json.dumps(message_data_dict)
    logger.info("[serviceA:produce_message] Serialized message: %s", serialized_message)


    if not await message_publisher.publish(serialized_message):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to publish the message")

    return {"status": "success", "detail": "Message queued"}
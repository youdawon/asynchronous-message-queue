import redis.asyncio as redis

from src.message_queue.redis_queue import RedisQueue
from src.utils.config import REDIS_QUEUE_NAME, MESSAGE_FILTER_TYPE
from src.utils.logger import logger

class MessageSubscriber:
    def __init__(self, redis_queue:RedisQueue = None):
        self.redis_queue = redis_queue or RedisQueue(REDIS_QUEUE_NAME)

    async def connect(self):
        return await self.redis_queue.connect()
    
    async def disconnect(self):
        await self.redis_queue.disconnect()

    async def subscribe(self):
        try:
            logger.info("[MessageSubscriber:subscribe] execute subscribe")                
            deserialized_message = await self.redis_queue.subscribe()
            if deserialized_message:
                if is_allowed_message_type(deserialized_message):
                    logger.info("[MessageSubscriber:subscribe] Consumed a message: %s", deserialized_message)                                    
                    return deserialized_message
                else:
                    return None            
        except Exception as e:
            logger.error("[MessageSubscriber:subscribe] Exception : %s", e)            
            return None
            
def is_allowed_message_type(message: dict) -> bool:
    if MESSAGE_FILTER_TYPE == "allow_all":
        return True
    elif MESSAGE_FILTER_TYPE == "specific_type":
        return message.get("type") == "serviceB"
    else:
        return False
import redis.asyncio as redis

from src.message_queue.redis_queue import RedisQueue
from src.utils.config import REDIS_MESSAGE_QUEUE_NAME, MESSAGE_FILTER_MODE, ALLOWED_TYPE
from src.utils.logger import logger

class MessageSubscriber:
    def __init__(self, redis_queue: RedisQueue=None, filter_mode=MESSAGE_FILTER_MODE):
        self.redis_queue = redis_queue or RedisQueue(REDIS_MESSAGE_QUEUE_NAME)
        self.filter_mode = filter_mode

    async def connect(self):
        return await self.redis_queue.connect()
    
    async def disconnect(self):
        await self.redis_queue.disconnect()

    async def subscribe(self):
        try:
            logger.info("[MessageSubscriber:subscribe] execute subscribe")                
            deserialized_message = await self.redis_queue.subscribe()
            if deserialized_message:
                if self.is_allowed_message_type(deserialized_message):
                    logger.info("[MessageSubscriber:subscribe] Consumed a message: %s", deserialized_message)                                    
                    return deserialized_message
                else:
                    return None            
        except Exception as e:
            logger.error("[MessageSubscriber:subscribe] Exception : %s", e)            
            return None
            
    def is_allowed_message_type(self, message):
        if self.filter_mode == "allow_all":
            return True
        elif self.filter_mode == "specific_type":
            return message.get("type") == ALLOWED_TYPE
        else:
            return False

from src.message_queue.redis_queue import RedisQueue
from src.utils.logger import logger
from src.utils.config import REDIS_QUEUE_NAME

class MessagePublisher:
    def __init__(self, redis_queue=None):
        self.redis_queue = redis_queue or RedisQueue(REDIS_QUEUE_NAME)

    async def connect(self):
        return await self.redis_queue.connect()

    async def disconnect(self):
        return await self.redis_queue.disconnect()        

    async def publish(self, serialized_message):
        logger.info("[MessagePublisher:publish] execute publish")        
        if await self.redis_queue.publish(serialized_message):
            logger.info("[MessagePublisher:publish] produced a message : %s, queue size : %s", serialized_message, await self.redis_queue.get_queue_size())
            return True
        else:
            logger.error("[MessagePublisher:publish] failed to publish a message %s", serialized_message)
            return False
import redis.asyncio as redis
import asyncio
import json
from redis.exceptions import RedisError

from src.utils.logger import logger
from src.utils.config import REDIS_CONNECTION_URL, REDIS_MAX_RETRIES, REDIS_RETRY_DELAY_SECONDS, REDIS_MESSAGE_QUEUE_MAX_SIZE, REDIS_MESSAGE_SUBSCRIBE_TIMEOUT_SECONDS

class RedisQueue:
    def __init__(self, queue_name=None, 
                 redis_client=REDIS_CONNECTION_URL, 
                 max_retries=REDIS_MAX_RETRIES, 
                 retry_delay=REDIS_RETRY_DELAY_SECONDS, 
                 connection_url=REDIS_CONNECTION_URL, 
                 max_queue_size=REDIS_MESSAGE_QUEUE_MAX_SIZE):
        
        self.redis_client = redis_client
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_url = connection_url
        self.max_queue_size = max_queue_size

    async def connect(self):
        for retry in range(1, self.max_retries + 1):
            try:
                self.redis_client = await redis.from_url(self.connection_url)
                logger.info("[RedisQueue:connect] Connected to Redis successfully")
                return True
            except Exception as e:
                logger.error("[RedisQueue:connect] Redis connection failed: %s", e)
                if retry < self.max_retries:
                    logger.info("[RedisQueue:connect] Retrying in %d seconds...", self.retry_delay)
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("[RedisQueue:connect] All %d attempts failed.", self.max_retries)
                    self.redis_client = None
                    return False

    async def disconnect(self):
        if not self.redis_client:
            logger.error("[RedisQueue:disconnect] Redis is not connected.")
            return False
        try:
            await self.redis_client.aclose()
            logger.info("[RedisQueue:disconnect] Disconnected from Redis successfully")
            return True
        except Exception as e:
            logger.error("[RedisQueue:disconnect] Failed to disconnect from Redis: %s", e)
            return False

    async def publish(self, serialized_message):
        for retry in range(1, self.max_retries + 1):
            try:
                await self.redis_client.rpush(self.queue_name, serialized_message)
                await self.redis_client.ltrim(self.queue_name, -self.max_queue_size, -1)
                logger.info("[RedisQueue:publish] Produced a message. queue name: %s, message: %s",
                            self.queue_name, serialized_message)
                logger.debug("[RedisQueue:publish] Produced a message. queue size: %s", await self.get_queue_size())
                return True
            except Exception as e:
                logger.error("[RedisQueue:publish] Failed to publish a message: %s", e)
                if retry < self.max_retries:
                    logger.info("[RedisQueue:publish] Retrying in %d seconds...", self.retry_delay)
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("[RedisQueue:publish] All %d attempts failed.", self.max_retries)
                    return False
    
    """
    Retries are handled by the polling loop in the WebSocket endpoint.
    """    
    async def subscribe(self, subscribe_timeout=REDIS_MESSAGE_SUBSCRIBE_TIMEOUT_SECONDS):
        try:
            response = await self.redis_client.brpop(self.queue_name, timeout=subscribe_timeout)
            if response:
                queue_name, message = response
                deserialized_message = json.loads(message)
                logger.info("[RedisQueue:subscribe] Consumed a message. queue name: %s, message: %s",
                            self.queue_name, response)
                return deserialized_message
            logger.info("[RedisQueue:subscribe] No message found in queue.")
            return None
        except Exception as e:
            logger.error("[RedisQueue:subscribe] Failed to subscribe a message: %s", e)
            return None

    async def get_queue_size(self):
        try:
            return await self.redis_client.llen(self.queue_name)
        except Exception as e:
            logger.error("[RedisQueue:get_queue_size] Failed to get queue size: %s", e)
            return 0
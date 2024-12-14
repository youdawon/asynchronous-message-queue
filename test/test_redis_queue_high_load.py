import pytest
import json
import asyncio
import redis.asyncio as redis
from redis.exceptions import RedisError
from src.message_queue.redis_queue import RedisQueue 

VALID_CONNECTION_URL="redis://localhost"
REDIS_MESSAGE_QUEUE_MAX_SIZE=1000
VALID_TEST_MESSAGE=json.dumps({"type": "test", "content": "test_message"})
REDIS_MESSAGE_QUEUE_NAME="test_queue"

@pytest.mark.asyncio
async def test_high_load_publishing():

    redis_client = redis.from_url(VALID_CONNECTION_URL)
    queue = RedisQueue(REDIS_MESSAGE_QUEUE_NAME, redis_client=redis_client, max_queue_size=REDIS_MESSAGE_QUEUE_MAX_SIZE)

    await queue.connect()

    await redis_client.delete(REDIS_MESSAGE_QUEUE_NAME)

    for _ in range(1000):
        await queue.publish(VALID_TEST_MESSAGE)

    queue_size = await queue.get_queue_size()

    assert queue_size == 1000, f"Queue size should be 1000, but got {queue_size}"

    await redis_client.delete(REDIS_MESSAGE_QUEUE_NAME)

    await queue.disconnect()
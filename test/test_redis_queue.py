import pytest
import json
from unittest.mock import AsyncMock, patch
from redis.exceptions import RedisError
from src.message_queue.redis_queue import RedisQueue 

VALID_CONNECTION_URL="redis://localhost"
REDIS_MAX_RETRIES=3
REDIS_MESSAGE_SUBSCRIBE_TIMEOUT_SECONDS=5
REDIS_MESSAGE_QUEUE_MAX_SIZE=5
VALID_TEST_MESSAGE=json.dumps({"type": "test", "content": "test_message"})
REDIS_MESSAGE_QUEUE_NAME="test_queue"
REDIS_RETRY_DELAY_SECONDS=0.1

@pytest.mark.asyncio
async def test_publish():
    redis_mock = AsyncMock()
    queue = RedisQueue(REDIS_MESSAGE_QUEUE_NAME, redis_client=redis_mock)    
    redis_mock.rpush.return_value = 1

    await queue.publish(VALID_TEST_MESSAGE)

    redis_mock.rpush.assert_called_with(REDIS_MESSAGE_QUEUE_NAME, VALID_TEST_MESSAGE)


@pytest.mark.asyncio
async def test_full_queue_handling():
    redis_mock = AsyncMock()
    queue = RedisQueue(REDIS_MESSAGE_QUEUE_NAME, redis_client=redis_mock, max_queue_size=REDIS_MESSAGE_QUEUE_MAX_SIZE)   
    redis_mock.llen.return_value = REDIS_MESSAGE_QUEUE_MAX_SIZE + 1

    await queue.publish(VALID_TEST_MESSAGE)

    redis_mock.ltrim.assert_called_with(REDIS_MESSAGE_QUEUE_NAME, -REDIS_MESSAGE_QUEUE_MAX_SIZE, -1)


@pytest.mark.asyncio
async def test_publish_retry_on_disconnect_and_timeout():
    redis_mock = AsyncMock()
    queue = RedisQueue(REDIS_MESSAGE_QUEUE_NAME, redis_client=redis_mock, max_retries=REDIS_MAX_RETRIES, retry_delay=REDIS_RETRY_DELAY_SECONDS)
    
    redis_mock.rpush.side_effect = [RedisError("Connection lost"), TimeoutError("Timeout occurred"), None]

    result = await queue.publish("test_message")
    
    assert result is True
    assert redis_mock.rpush.call_count == REDIS_MAX_RETRIES


@pytest.mark.asyncio
async def test_subscribe():
    redis_mock = AsyncMock()
    queue = RedisQueue(REDIS_MESSAGE_QUEUE_NAME, redis_client=redis_mock)
    redis_mock.brpop.return_value = (REDIS_MESSAGE_QUEUE_NAME, VALID_TEST_MESSAGE)
    
    result = await queue.subscribe()

    assert result == json.loads(VALID_TEST_MESSAGE)
    redis_mock.brpop.assert_called_with(REDIS_MESSAGE_QUEUE_NAME, timeout=REDIS_MESSAGE_SUBSCRIBE_TIMEOUT_SECONDS)


@pytest.mark.asyncio
async def test_subscribe_timeout():
    redis_mock = AsyncMock()
    queue = RedisQueue(REDIS_MESSAGE_QUEUE_NAME, redis_client=redis_mock)
    redis_mock.brpop.side_effect = TimeoutError("Timeout occurred")  

    result = await queue.subscribe()
    
    assert result is None

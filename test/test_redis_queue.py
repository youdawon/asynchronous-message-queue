import pytest
import json
from unittest.mock import AsyncMock, patch
from redis.exceptions import RedisError
from src.message_queue.redis_queue import RedisQueue 

VALID_CONNECTION_URL="redis://localhost"
REDIS_RETRY_COUNT=3
REDIS_SUBSCRIBE_TIMEOUT=5
REDIS_MAX_QUEUE_SIZE=5
VALID_TEST_MESSAGE=json.dumps({"type": "test", "content": "test_message"})
QUEUE_NAME="test_queue"
RETRY_DELAY=0.1

@pytest.mark.asyncio
async def test_connect_success():
    redis_mock = AsyncMock()
    redis_mock.from_url.return_value = redis_mock

    with patch("src.message_queue.redis_queue.redis", redis_mock):
        queue = RedisQueue(QUEUE_NAME, connection_url=VALID_CONNECTION_URL)
        result = await queue.connect()

        assert result is True
        redis_mock.from_url.assert_called_once_with(VALID_CONNECTION_URL)

@pytest.mark.asyncio
async def test_connect_retries_on_failure():
    redis_mock = AsyncMock()    
    redis_mock.from_url.side_effect = RedisError("Connection failed")
    with patch("src.message_queue.redis_queue.redis", redis_mock):
        queue = RedisQueue(QUEUE_NAME, max_retries=REDIS_RETRY_COUNT, connection_url=VALID_CONNECTION_URL)
        result = await queue.connect()

        assert redis_mock.from_url.call_count == REDIS_RETRY_COUNT        
        

@pytest.mark.asyncio
async def test_publish():
    redis_mock = AsyncMock()
    queue = RedisQueue(QUEUE_NAME, redis_client=redis_mock)
    redis_mock.rpush.return_value = 1 
    
    await queue.publish(VALID_TEST_MESSAGE)

    redis_mock.rpush.assert_called_with(QUEUE_NAME, VALID_TEST_MESSAGE)


@pytest.mark.asyncio
async def test_full_queue_handling():
    redis_mock = AsyncMock()
    queue = RedisQueue(QUEUE_NAME, redis_client=redis_mock, max_queue_size=REDIS_MAX_QUEUE_SIZE)

    redis_mock.llen.return_value = REDIS_MAX_QUEUE_SIZE + 1
    await queue.publish(VALID_TEST_MESSAGE)
    redis_mock.ltrim.assert_called_with(QUEUE_NAME, -REDIS_MAX_QUEUE_SIZE, -1) 


@pytest.mark.asyncio
async def test_publish_retry_on_disconnect():
    redis_mock = AsyncMock()
    queue = RedisQueue(QUEUE_NAME, redis_client=redis_mock, max_retries=REDIS_RETRY_COUNT, retry_delay=RETRY_DELAY)

    redis_mock.rpush.side_effect = RedisError("Connection lost")
    result = await queue.publish("test_message")

    assert result is False
    assert redis_mock.rpush.call_count == REDIS_RETRY_COUNT  


@pytest.mark.asyncio
async def test_publish_timeout():
    redis_mock = AsyncMock()
    queue = RedisQueue(QUEUE_NAME, redis_client=redis_mock)

    redis_mock.rpush.side_effect = TimeoutError("Timeout occurred")
    with pytest.raises(TimeoutError):
        await queue.publish(VALID_TEST_MESSAGE)    


@pytest.mark.asyncio
async def test_subscribe():
    redis_mock = AsyncMock()
    queue = RedisQueue(QUEUE_NAME, redis_client=redis_mock)
    redis_mock.brpop.return_value = (QUEUE_NAME, VALID_TEST_MESSAGE)

    result = await queue.subscribe()

    assert result == json.loads(VALID_TEST_MESSAGE)
    redis_mock.brpop.assert_called_with(QUEUE_NAME, timeout=REDIS_SUBSCRIBE_TIMEOUT)


@pytest.mark.asyncio
async def test_subscribe_timeout():
    redis_mock = AsyncMock()
    queue = RedisQueue(QUEUE_NAME, redis_client=redis_mock)

    redis_mock.brpop.side_effect = TimeoutError("Timeout occurred")  
    with pytest.raises(TimeoutError):
        await queue.subscribe()


@pytest.mark.asyncio
async def test_get_queue_size():
    redis_mock = AsyncMock()
    queue = RedisQueue(QUEUE_NAME, redis_client=redis_mock)
    redis_mock.llen.return_value = 5

    size = await queue.get_queue_size()

    redis_mock.llen.assert_called_with(QUEUE_NAME)
    assert size == 5


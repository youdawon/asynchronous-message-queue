import pytest
import asyncio
import os
import redis.asyncio as redis
import json
import logging
from src.message_queue.redis_queue import RedisQueue

VALID_CONNECTION_URL = "redis://localhost:6379"
VALID_TEST_MESSAGE = json.dumps({"type": "test", "content": "test_message"})
REDIS_MESSAGE_QUEUE_NAME = "test_queue"
REDIS_MESSAGE_QUEUE_MAX_SIZE = 1000
MESSAGE_COUNT = 1000 
SEMAPHORE_VALUE = 100

LOG_DIR = "logs"
LOG_FILE = "logs/test_high_load_publishing_parallel.log"



"""
Test File: test_high_load_publishing_parallel.py

Description:
This file contains a high-load test for publishing messages to a Redis queue
using the RedisQueue class. The test evaluates both the queue's capacity to
handle a large number of parallel messages and calculates the throughput
(messages per second).

Prerequisites:
- Redis must be running and accessible at the configured URL (default: "redis://localhost:6379").
- The queue name and configuration constants should match the test requirements.

Environment:
Ensure that the Redis server is running locally or update `VALID_CONNECTION_URL`
to point to the correct Redis instance.

Usage:
Run this test using pytest:
    pytest test_high_load_publishing_parallel.py
"""

@pytest.mark.asyncio
async def test_high_load_publishing_parallel():

    logger = logging.getLogger("test_high_load_publishing_parallel")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    redis_client = redis.from_url(VALID_CONNECTION_URL)
    queue = RedisQueue(
        REDIS_MESSAGE_QUEUE_NAME,
        redis_client=redis_client,
        max_queue_size=REDIS_MESSAGE_QUEUE_MAX_SIZE
    )

    try:
        logger.info("Connecting to Redis...")
        await redis_client.ping()
        logger.info("Redis connection established.")
        await redis_client.delete(REDIS_MESSAGE_QUEUE_NAME)

        semaphore = asyncio.Semaphore(SEMAPHORE_VALUE)
        message_count = MESSAGE_COUNT
        logger.info("Starting test with %s messages...", message_count)

        async def publish_message(i):
            async with semaphore:
                try:
                    logger.info("Publishing message %s...", i)
                    result = await queue.publish(VALID_TEST_MESSAGE)
                    assert result is True
                except Exception as e:
                    logger.error("Error publishing message %s: %s", i, e)

        start_time = asyncio.get_event_loop().time()

        await asyncio.gather(*(publish_message(i) for i in range(message_count)))

        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time

        queue_size = await queue.get_queue_size()
        logger.info("Queue size after publishing: %s", queue_size)
        assert queue_size == min(message_count, REDIS_MESSAGE_QUEUE_MAX_SIZE)

        throughput = message_count / total_time
        logger.info(f"Test completed in {total_time:.2f} seconds.")
        logger.info(f"Throughput: {throughput:.2f} messages/second")

    finally:
        await redis_client.aclose()
        await queue.disconnect()
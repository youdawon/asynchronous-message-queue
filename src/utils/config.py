# Redis Configuration
REDIS_MESSAGE_QUEUE_NAME = "message_queue"  # The name of the Redis queue used for message storage.
REDIS_CONNECTION_URL = "redis://redis:6379"  # Redis server connection URL.
REDIS_MAX_RETRIES = 3  # Maximum number of retries when interacting with Redis.
REDIS_RETRY_DELAY_SECONDS = 2  # Delay (in seconds) between retry attempts.
REDIS_MESSAGE_QUEUE_MAX_SIZE = 50  # Maximum size of the Redis message queue.
REDIS_MESSAGE_SUBSCRIBE_TIMEOUT_SECONDS = 2  # Timeout for the Redis BRPOP operation in seconds.

# WebSocket Configuration
WEBSOCKET_MAX_RETRIES = 2  # Maximum number of retries for WebSocket connection attempts.
WEBSOCKET_POLL_INTERVAL_SECONDS = 2  # Interval (in seconds) between WebSocket polling attempts.
WEBSOCKET_RETRY_DELAY_SECONDS = 1  # Delay (in seconds) before retrying a failed WebSocket connection.

# Message Settings
MESSAGE_MAX_CONTENT_LENGTH = 512  # Maximum allowed length (in characters) for message content.


"""
MESSAGE_FILTER_MODE defines the message filtering behavior.

- "allow_all": Allows all messages to be processed, regardless of their type.
- "specific_type": Only processes messages where the 'type' parameter matches "serviceB".

Usage:
To filter messages by type, set the mode to "specific_type". 
In this case, only messages with a 'type' of "serviceB" will be forwarded. If you want to allow all messages, set the mode to "allow_all".
"""
MESSAGE_FILTER_MODE = "allow_all"
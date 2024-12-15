REDIS_MESSAGE_QUEUE_NAME = "message_queue"
REDIS_CONNECTION_URL = "redis://redis:6379"
REDIS_MAX_RETRIES = 2
REDIS_RETRY_DELAY_SECONDS = 2
REDIS_MESSAGE_QUEUE_MAX_SIZE = 10
REDIS_MESSAGE_SUBSCRIBE_TIMEOUT_SECONDS = 5

WEBSOCKET_MAX_RETRIES = 2
WEBSOCKET_POLL_INTERVAL_SECONDS = 2
WEBSOCKET_RETRY_DELAY_SECONDS = 0.5

MESSAGE_MAX_CONTENT_LENGTH = 256

"""
MESSAGE_FILTER_MODE defines the message filtering behavior.

- "allow_all": Allows all messages to be processed, regardless of their type.
- "specific_type": Only processes messages where the 'type' parameter matches "serviceB".

Usage:
To filter messages by type, set the mode to "specific_type". 
In this case, only messages with a 'type' of "serviceB" will be forwarded. If you want to allow all messages, set the mode to "allow_all".
"""
MESSAGE_FILTER_MODE = "allow_all"
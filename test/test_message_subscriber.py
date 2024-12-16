import pytest
from src.service_b.message_subscriber import MessageSubscriber
from src.utils.config import ALLOWED_TYPE

"""
MESSAGE_FILTER_MODE defines the message filtering behavior.

- "allow_all": Allows all messages to be processed, regardless of their type.
- "specific_type": Only processes messages where the 'type' parameter matches ALLOWED_TYPE.

Usage:
To filter messages by type, set the mode to "specific_type". 
In this case, only messages with a 'type' matching ALLOWED_TYPE will be forwarded. If you want to allow all messages, set the mode to "allow_all".
"""
@pytest.mark.parametrize(
    "message, filter_mode, expected",
    [
        ({"type": "type_test", "content": "test"}, "allow_all", True),  
        ({"type": ALLOWED_TYPE, "content": "test"}, "specific_type", True),  
        ({"type": "different_type", "content": "test"}, "specific_type", False), 
    ],
)
def test_is_allowed_message_type(message, filter_mode, expected):
    subscriber = MessageSubscriber(filter_mode=filter_mode)
    assert subscriber.is_allowed_message_type(message) == expected
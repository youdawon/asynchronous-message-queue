import pytest
from src.service_b.message_subscriber import MessageSubscriber

@pytest.mark.parametrize(
    "message, filter_mode, expected",
    [
        ({"type": "serviceA", "content": "test"}, "allow_all", True),
        ({"type": "serviceB", "content": "test"}, "specific_type", True),
        ({"type": "serviceA", "content": "test"}, "specific_type", False),
        ({"type": "unknown", "content": "test"}, "unknown_filter", False),
    ],
)
def test_is_allowed_message_type(message, filter_mode, expected):
    subscriber = MessageSubscriber(filter_mode=filter_mode)
    assert subscriber.is_allowed_message_type(message) == expected
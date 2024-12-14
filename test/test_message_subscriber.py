import pytest

from src.service_b.message_subscriber import is_allowed_message_type

@pytest.mark.parametrize(
    "message, filter_type, expected",
    [
        ({"type": "serviceA", "content": "test"}, "allow_all", True), 
        ({"type": "serviceB", "content": "test"}, "specific_type", True), 
        ({"type": "serviceA", "content": "test"}, "specific_type", False), 
        ({"type": "unknown", "content": "test"}, "unknown_filter", False),
    ],
)
def test_is_allowed_message_type(message, filter_type, expected, monkeypatch):
    monkeypatch.setattr("src.utils.config.MESSAGE_FILTER_TYPE", filter_type)
    assert is_allowed_message_type(message) == expected
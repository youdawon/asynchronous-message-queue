from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import json
from src.service_a.app import app, message_publisher

client = TestClient(app)

MESSAGE_MAX_CONTENT_LENGTH = 512

valid_payload={"type": "test", "content": "test queue"}

def test_produce_message_success():
    message_publisher.publish = AsyncMock(return_value=True)
    response = client.post("/messages", json=valid_payload)

    assert response.status_code == 200
    assert response.json() == {"status": "success", "detail": "Message queued"}
    message_publisher.publish.assert_called_once()

def test_produce_message_empty_content():
    payload = {"type": "test", "content": ""}
    response = client.post("/messages", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "message or type is empty"

def test_produce_message_empty_type():
    payload = {"type": "", "content": "test message"}
    response = client.post("/messages", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "message or type is empty"   

def test_produce_message_exceeding_max_length():
    payload = {"type": "test", "content": "a" * (MESSAGE_MAX_CONTENT_LENGTH + 1)}
    response = client.post("/messages", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "message is too long"

def test_produce_message_publish_failure():
    message_publisher.publish = AsyncMock(return_value=False)

    response = client.post("/messages", json=valid_payload)

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to publish the message"

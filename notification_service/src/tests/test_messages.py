# stdlib
import tempfile
from uuid import uuid4

# thirdparty
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_message(test_client: AsyncClient, headers):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    headers.pop("Content-Type", None)

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
        tmp_file.write(test_template_data["body"])
        tmp_file.seek(0)

        form_data = {
            "name": test_template_data["name"],
            "subject": test_template_data["subject"],
        }

        files = {"body": ("test.txt", tmp_file, "text/plain")}

        template_response = await test_client.post(
            "http://api:8000/api-notify/v1/templates/",
            data=form_data,
            files=files,
            headers=headers,
        )

    assert template_response.status_code == 201, template_response.text

    message_data = {
        "event_type": "user_registration",
        "template_id": template_response.json()["id"],
        "context": {"username": "test_user"},
        "subscribers": [str(uuid4())],
    }

    send_response = await test_client.post(
        "http://api:8000/api-notify/v1/messages/send-message/",
        json=message_data,
        headers=headers,
    )

    assert send_response.status_code == 201, send_response.text
    response_data = send_response.json()
    assert response_data["status"] == "success"
    assert response_data["queue"] == "notifications.high"
    assert response_data["priority"] == 5


@pytest.mark.asyncio
async def test_send_message_with_invalid_template(test_client: AsyncClient, headers):
    message_data = {
        "event_type": "user_registration",
        "template_id": str(uuid4()),
        "context": {"username": "test_user"},
        "subscribers": [str(uuid4())],
    }

    send_response = await test_client.post(
        "http://api:8000/api-notify/v1/messages/send-message/",
        json=message_data,
        headers=headers,
    )

    assert send_response.status_code == 404
    assert send_response.json()["detail"] == "Template not found"


@pytest.mark.asyncio
async def test_send_message_with_empty_subscribers(test_client: AsyncClient, headers):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    headers.pop("Content-Type", None)

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
        tmp_file.write(test_template_data["body"])
        tmp_file.seek(0)

        form_data = {
            "name": test_template_data["name"],
            "subject": test_template_data["subject"],
        }

        files = {"body": ("test.txt", tmp_file, "text/plain")}

        template_response = await test_client.post(
            "http://api:8000/api-notify/v1/templates/",
            data=form_data,
            files=files,
            headers=headers,
        )

    assert template_response.status_code == 201, template_response.text

    message_data = {
        "event_type": "user_registration",
        "template_id": template_response.json()["id"],
        "context": {"username": "test_user"},
        "subscribers": [],
    }

    send_response = await test_client.post(
        "http://api:8000/api-notify/v1/messages/send-message/",
        json=message_data,
        headers=headers,
    )

    assert send_response.status_code == 201


@pytest.mark.asyncio
async def test_send_message_with_invalid_event_type(test_client: AsyncClient, create_template, headers):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)

    message_data = {
        "event_type": "invalid_event_type",
        "template_id": template["id"],
        "context": {"username": "test_user"},
        "subscribers": [str(uuid4())],
    }

    send_response = await test_client.post(
        "http://api:8000/api-notify/v1/messages/send-message/",
        json=message_data,
        headers=headers,
    )

    assert send_response.status_code == 422
    assert "event_type" in send_response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_send_message_with_missing_required_fields(test_client: AsyncClient, headers):
    message_data = {
        "context": {"username": "test_user"},
        "subscribers": [str(uuid4())],
    }

    send_response = await test_client.post(
        "http://api:8000/api-notify/v1/messages/send-message/",
        json=message_data,
        headers=headers,
    )

    assert send_response.status_code == 422
    errors = send_response.json()["detail"]
    assert any("event_type" in error["loc"] for error in errors)
    assert any("template_id" in error["loc"] for error in errors)

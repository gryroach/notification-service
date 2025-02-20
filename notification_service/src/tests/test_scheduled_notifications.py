# stdlib
from datetime import datetime, timezone

# thirdparty
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_scheduled_notification(
    test_client: AsyncClient, create_template, headers
):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)
    template_id = template["id"]

    scheduled_data = {
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template_id,
        "channel_type": "email",
        "event_type": "custom",
        "scheduled_time": datetime.now(timezone.utc).isoformat(),
        "is_sent": False,
    }

    scheduled_response = await test_client.post(
        "http://api:8000/api-notify/v1/scheduled/",
        json=scheduled_data,
        headers=headers,
    )

    assert scheduled_response.status_code == 201, scheduled_response.text
    scheduled_notification = scheduled_response.json()

    response = await test_client.get(
        f"http://api:8000/api-notify/v1/scheduled/{scheduled_notification['id']}",
        headers=headers,
    )
    assert response.status_code == 200, response.json()
    assert response.json()["id"] == scheduled_notification["id"]
    assert response.json()["template_id"] == template_id
    assert response.json()["channel_type"] == "email"
    assert response.json()["event_type"] == "custom"
    assert response.json()["is_sent"] is False


@pytest.mark.asyncio
async def test_update_scheduled_notification(
    test_client: AsyncClient, create_template, headers
):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)
    template_id = template["id"]

    scheduled_data = {
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template_id,
        "channel_type": "email",
        "event_type": "custom",
        "scheduled_time": datetime.now(timezone.utc).isoformat(),
        "is_sent": False,
    }

    scheduled_response = await test_client.post(
        "http://api:8000/api-notify/v1/scheduled/",
        json=scheduled_data,
        headers=headers,
    )

    assert scheduled_response.status_code == 201, scheduled_response.text
    scheduled_notification = scheduled_response.json()

    update_data = {
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template_id,
        "channel_type": "sms",
        "event_type": "custom",
        "scheduled_time": datetime.now(timezone.utc).isoformat(),
        "is_sent": True,
    }

    update_response = await test_client.put(
        f"http://api:8000/api-notify/v1/scheduled/{scheduled_notification['id']}",
        json=update_data,
        headers=headers,
    )

    assert update_response.status_code == 200, update_response.text
    updated_notification = update_response.json()
    assert updated_notification["channel_type"] == "sms"
    assert updated_notification["is_sent"] is True


@pytest.mark.asyncio
async def test_delete_scheduled_notification(
    test_client: AsyncClient, create_template, headers
):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)
    template_id = template["id"]

    scheduled_data = {
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template_id,
        "channel_type": "email",
        "event_type": "custom",
        "scheduled_time": datetime.now(timezone.utc).isoformat(),
        "is_sent": False,
    }

    scheduled_response = await test_client.post(
        "http://api:8000/api-notify/v1/scheduled/",
        json=scheduled_data,
        headers=headers,
    )

    assert scheduled_response.status_code == 201, scheduled_response.text
    scheduled_notification = scheduled_response.json()

    delete_response = await test_client.delete(
        f"http://api:8000/api-notify/v1/scheduled/{scheduled_notification['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 204, delete_response.text

    get_response = await test_client.get(
        f"http://api:8000/api-notify/v1/scheduled/{scheduled_notification['id']}",
        headers=headers,
    )

    assert get_response.status_code == 404, get_response.text

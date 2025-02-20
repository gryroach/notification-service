# thirdparty
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_periodic_notification(
    test_client: AsyncClient, create_template, headers
):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)

    periodic_data = {
        "staff_id": "550e8400-e29b-41d4-a716-446655440000",
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template["id"],
        "channel_type": "email",
        "cron_schedule": "* * * * *",
        "event_type": "custom",
    }

    periodic_response = await test_client.post(
        "http://api:8000/api-notify/v1/periodic/",
        json=periodic_data,
        headers=headers,
    )

    assert periodic_response.status_code == 201, periodic_response.text
    periodic_notification = periodic_response.json()

    response = await test_client.get(
        f"http://api:8000/api-notify/v1/periodic/{periodic_notification['id']}",
        headers=headers,
    )
    assert response.status_code == 200, response.json()


@pytest.mark.asyncio
async def test_update_periodic_notification(
    test_client: AsyncClient, create_template, headers
):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)

    periodic_data = {
        "staff_id": "550e8400-e29b-41d4-a716-446655440000",
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template["id"],
        "channel_type": "email",
        "cron_schedule": "* * * * *",
        "event_type": "custom",
    }

    create_response = await test_client.post(
        "http://api:8000/api-notify/v1/periodic/",
        json=periodic_data,
        headers=headers,
    )
    assert create_response.status_code == 201
    notification_id = create_response.json()["id"]

    update_data = {
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template["id"],
        "channel_type": "sms",
        "cron_schedule": "0 * * * *",
        "event_type": "user_registration",
    }

    update_response = await test_client.put(
        f"http://api:8000/api-notify/v1/periodic/{notification_id}",
        json=update_data,
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_notification = update_response.json()
    assert updated_notification["channel_type"] == "sms"
    assert updated_notification["cron_schedule"] == "0 * * * *"
    assert updated_notification["event_type"] == "user_registration"


@pytest.mark.asyncio
async def test_delete_periodic_notification(
    test_client: AsyncClient, create_template, headers
):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)

    periodic_data = {
        "staff_id": "550e8400-e29b-41d4-a716-446655440000",
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template["id"],
        "channel_type": "email",
        "cron_schedule": "* * * * *",
        "event_type": "custom",
    }

    create_response = await test_client.post(
        "http://api:8000/api-notify/v1/periodic/",
        json=periodic_data,
        headers=headers,
    )
    assert create_response.status_code == 201
    notification_id = create_response.json()["id"]

    delete_response = await test_client.delete(
        f"http://api:8000/api-notify/v1/periodic/{notification_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    get_response = await test_client.get(
        f"http://api:8000/api-notify/v1/periodic/{notification_id}",
        headers=headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_periodic_notification_with_invalid_template(
    test_client: AsyncClient, headers
):
    periodic_data = {
        "staff_id": "550e8400-e29b-41d4-a716-446655440000",
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": "550e8400-e29b-41d4-a716-446655440000",
        "channel_type": "email",
        "cron_schedule": "* * * * *",
        "event_type": "custom",
    }

    response = await test_client.post(
        "http://api:8000/api-notify/v1/periodic/",
        json=periodic_data,
        headers=headers,
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, str)
    assert "Указанная связанная запись не существует" in error_detail


@pytest.mark.asyncio
async def test_create_periodic_notification_with_invalid_cron(
    test_client: AsyncClient, create_template, headers
):
    test_template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_template_data)

    periodic_data = {
        "staff_id": "550e8400-e29b-41d4-a716-446655440000",
        "subscriber_query_type": "birthday_today",
        "subscriber_query_params": None,
        "template_id": template["id"],
        "channel_type": "email",
        "cron_schedule": "invalid_cron",
        "event_type": "custom",
    }

    response = await test_client.post(
        "http://api:8000/api-notify/v1/periodic/",
        json=periodic_data,
        headers=headers,
    )
    assert response.status_code == 422
    assert "cron_schedule" in response.json()["detail"][0]["loc"]

# stdlib
import tempfile
from uuid import uuid4

# thirdparty
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_template(test_client: AsyncClient, create_template, headers):
    test_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    template = await create_template(test_data)

    get_response = await test_client.get(
        f"http://api:8000/api-notify/v1/templates/{template['id']}",
        headers=headers,
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == template["id"]
    assert get_response.json()["name"] == test_data["name"]
    assert get_response.json()["subject"] == test_data["subject"]
    assert get_response.json()["body"] == test_data["body"]


@pytest.mark.asyncio
async def test_update_template(test_client: AsyncClient, headers):
    test_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    headers.pop("Content-Type", None)

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
        tmp_file.write(test_data["body"])
        tmp_file.seek(0)

        form_data = {
            "name": test_data["name"],
            "subject": test_data["subject"],
        }

        files = {"body": ("test.txt", tmp_file, "text/plain")}

        response = await test_client.post(
            "http://api:8000/api-notify/v1/templates/",
            data=form_data,
            files=files,
            headers=headers,
        )

    assert response.status_code == 201
    template = response.json()

    update_data = {
        "name": "Updated Template",
        "subject": "Updated Subject",
        "body": "Updated Body",
    }

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
        tmp_file.write(update_data["body"])
        tmp_file.seek(0)

        form_data = {
            "name": update_data["name"],
            "subject": update_data["subject"],
        }

        files = {"body": ("updated.txt", tmp_file, "text/plain")}

        update_response = await test_client.put(
            f"http://api:8000/api-notify/v1/templates/{template['id']}",
            data=form_data,
            files=files,
            headers=headers,
        )

    assert update_response.status_code == 200
    updated_template = update_response.json()
    assert updated_template["name"] == update_data["name"]
    assert updated_template["subject"] == update_data["subject"]
    assert updated_template["body"] == update_data["body"]


@pytest.mark.asyncio
async def test_delete_template(test_client: AsyncClient, headers):
    test_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    headers.pop("Content-Type", None)

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
        tmp_file.write(test_data["body"])
        tmp_file.seek(0)

        form_data = {
            "name": test_data["name"],
            "subject": test_data["subject"],
        }

        files = {"body": ("test.txt", tmp_file, "text/plain")}

        response = await test_client.post(
            "http://api:8000/api-notify/v1/templates/",
            data=form_data,
            files=files,
            headers=headers,
        )

    assert response.status_code == 201
    template = response.json()

    delete_response = await test_client.delete(
        f"http://api:8000/api-notify/v1/templates/{template['id']}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = await test_client.get(
        f"http://api:8000/api-notify/v1/templates/{template['id']}",
        headers=headers,
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_templates(test_client: AsyncClient, headers):
    test_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "body": "Test Body",
    }

    headers.pop("Content-Type", None)

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
        tmp_file.write(test_data["body"])
        tmp_file.seek(0)

        form_data = {
            "name": test_data["name"],
            "subject": test_data["subject"],
        }

        files = {"body": ("test.txt", tmp_file, "text/plain")}

        await test_client.post(
            "http://api:8000/api-notify/v1/templates/",
            data=form_data,
            files=files,
            headers=headers,
        )

    response = await test_client.get(
        "http://api:8000/api-notify/v1/templates/",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

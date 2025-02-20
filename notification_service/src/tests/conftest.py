# stdlib
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

# thirdparty
import jwt
import pytest
from httpx import AsyncClient


@pytest.fixture
async def test_client():
    async with AsyncClient() as client:
        yield client


@pytest.fixture(scope="session")
def valid_token():
    private_key_path = Path("/app") / "tools" / "keys" / "example_private_key.pem"
    with open(private_key_path) as key_file:
        private_key = key_file.read()

    now = datetime.now(UTC)
    payload = {
        "user": str(uuid4()),
        "session_version": 1,
        "iat": now,
        "exp": now + timedelta(days=7),
        "role": "staff_user",
        "type": "access",
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


@pytest.fixture
def headers(valid_token):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json",
        "X-Request-Id": str(uuid4()),
        "X-User-Id": "d1a61b2a-7a4b-4a8e-b5c2-1f3a7d5b8e9c",
    }


@pytest.fixture
async def create_template(test_client: AsyncClient, headers):
    async def _create_template(template_data: dict):
        headers.pop("Content-Type", None)

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
            tmp_file.write(template_data["body"])
            tmp_file.seek(0)

            form_data = {
                "name": template_data["name"],
                "subject": template_data["subject"],
            }

            files = {"body": ("test.txt", tmp_file, "text/plain")}

            response = await test_client.post(
                "http://api:8000/api-notify/v1/templates/",
                data=form_data,
                files=files,
                headers=headers,
            )
            assert response.status_code == 201
            return response.json()

    return _create_template

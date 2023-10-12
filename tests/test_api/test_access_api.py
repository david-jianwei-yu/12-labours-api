import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        return client


@pytest.fixture
def token(client):
    dummy_data = {
        "email": "dummy_email@gmail.com",
        "machine": "dummy_machine_id",
        "expiration": "dummy_expiration_time",
    }
    response = client.post("/access/token", json=dummy_data)
    return response.json()


def test_create_access(client):
    missing_data = {}
    response = client.post("/access/token", json=missing_data)
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Missing one or more fields in the request body"

    dummy_data = {
        "email": "dummy_email@gmail.com",
        "machine": "dummy_machine_id",
        "expiration": "dummy_expiration_time",
    }
    response = client.post("/access/token", json=dummy_data)
    result = response.json()
    assert response.status_code == 200
    assert "access_token" in result


def test_create_one_off_access(client, token):
    response = client.get(
        "/access/oneoff",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert "one_off_token" in result


def test_revoke_access(client, token):
    response = client.delete(
        "/access/revoke",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert result["message"] == "Unable to remove default access authority"

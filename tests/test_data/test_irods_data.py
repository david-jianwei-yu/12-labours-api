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


def test_irods_collection(client, token):
    payload1 = {"path": "/dataset-217-version-2"}
    response = client.post(
        "/collection",
        json=payload1,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert result["folders"] == [
        {"name": "derivative", "path": "/dataset-217-version-2/derivative"},
        {"name": "primary", "path": "/dataset-217-version-2/primary"},
    ]
    assert result["files"] == [
        {
            "name": "dataset_description_gen3.json",
            "path": "/dataset-217-version-2/dataset_description_gen3.json",
        },
        {
            "name": "dataset_description.xlsx",
            "path": "/dataset-217-version-2/dataset_description.xlsx",
        },
        {
            "name": "manifest_gen3.json",
            "path": "/dataset-217-version-2/manifest_gen3.json",
        },
    ]

    payload2 = {"path": "/dataset-46-version-2"}
    response = client.post(
        "/collection",
        json=payload2,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert result["folders"] == [
        {"name": "derivative", "path": "/dataset-46-version-2/derivative"},
        {"name": "docs", "path": "/dataset-46-version-2/docs"},
        {"name": "primary", "path": "/dataset-46-version-2/primary"},
        {"name": "source", "path": "/dataset-46-version-2/source"},
    ]
    assert result["files"] == [
        {
            "name": "dataset_description.json",
            "path": "/dataset-46-version-2/dataset_description.json",
        },
        {
            "name": "dataset_description.xlsx",
            "path": "/dataset-46-version-2/dataset_description.xlsx",
        },
        {"name": "experiment.json", "path": "/dataset-46-version-2/experiment.json"},
        {
            "name": "manifest_gen3.json",
            "path": "/dataset-46-version-2/manifest_gen3.json",
        },
        {"name": "manifest.xlsx", "path": "/dataset-46-version-2/manifest.xlsx"},
        {"name": "subjects.json", "path": "/dataset-46-version-2/subjects.json"},
        {"name": "subjects.xlsx", "path": "/dataset-46-version-2/subjects.xlsx"},
    ]

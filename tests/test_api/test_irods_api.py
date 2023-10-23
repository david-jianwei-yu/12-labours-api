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


@pytest.fixture
def one_off_token(client, token):
    response = client.get(
        "/access/oneoff",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    return response.json()


def test_get_irods_collection(client, token):
    pass_case_root = {}
    response = client.post(
        "/collection",
        json=pass_case_root,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert len(response.json()) == 2

    pass_case_sub = {"path": "/dataset-217-version-2"}
    response = client.post(
        "/collection",
        json=pass_case_sub,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert len(response.json()) == 2

    empty_string_path = {"path": ""}
    response = client.post(
        "/collection",
        json=empty_string_path,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid path format is used"

    wrong_path = {"path": "/dataset-217-version-2/dummy_filename"}
    response = client.post(
        "/collection",
        json=wrong_path,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Data not found in the provided path"

    no_access_case = {"path": "/dataset-12L_0-version-1"}
    response = client.post(
        "/collection",
        json=no_access_case,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "Unable to access the data"


def test_get_irods_data_file(client, one_off_token):
    ACTION = "preview"
    FILEPATH = "dataset-217-version-2/derivative/scaffold_context_info.json"
    response = client.get(
        f"/data/{ACTION}/{FILEPATH}?token={one_off_token['one_off_token']}"
    )
    result = response.json()
    assert response.status_code == 200
    assert (
        result["description"]
        == "Annotated brainstem scaffold for pig available for registration of segmented neural anatomical-functional mapping of neural circuits."
    )
    assert result["heading"] == "Generic pig brainstem scaffold"

    ACTION = "preview"
    INVALID_FILEPATH = "dataset-217-version-2/derivative/scaffold_context_info"
    response = client.get(
        f"/data/{ACTION}/{INVALID_FILEPATH}?token={one_off_token['one_off_token']}"
    )
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Data not found in the provided path"

    ACTION = "preview"
    INVALID_FILEPATH = "dataset-12L_0-version-1/dummy_filename"
    response = client.get(
        f"/data/{ACTION}/{INVALID_FILEPATH}?token={one_off_token['one_off_token']}"
    )
    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "Unable to access the data"

    INVALID_ACTION = "preload"
    FILEPATH = "dataset-217-version-2/derivative/scaffold_context_info.json"
    response = client.get(
        f"/data/{INVALID_ACTION}/{FILEPATH}?token={one_off_token['one_off_token']}"
    )
    result = response.json()
    assert response.status_code == 422
    # assert response.status_code == 405
    # assert result["detail"] == "The action is not provided in this API"

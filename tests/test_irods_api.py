import pytest
from app import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as client:
        return client


def test_get_irods_collection(client):
    pass_case_root = {}
    response = client.post("/collection", json=pass_case_root)
    result = response.json()
    assert response.status_code == 200
    assert len(response.json()) == 2

    pass_case_sub = {
        "path": "/dataset-217-version-2"
    }
    response = client.post("/collection", json=pass_case_sub)
    result = response.json()
    assert response.status_code == 200
    assert len(response.json()) == 2

    empty_string_path = {
        "path": ""
    }
    response = client.post("/collection", json=empty_string_path)
    result = response.json()
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid path format is used"

    wrong_path = {
        "path": "/dummy/folder/path"
    }
    response = client.post("/collection", json=wrong_path)
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Data not found in the provided path"


def test_get_irods_data_file(client):
    ACTION = "preview"
    FILEPATH = "dataset-217-version-2/derivative/scaffold_context_info.json"
    response = client.get(f"/data/{ACTION}/{FILEPATH}")
    result = response.json()
    assert response.status_code == 200
    assert result["description"] == "Annotated brainstem scaffold for pig available for registration of segmented neural anatomical-functional mapping of neural circuits."
    assert result["heading"] == "Generic pig brainstem scaffold"

    ACTION = "preview"
    INVALID_FILEPATH = "dataset-217-version-2/derivative/scaffold_context_info"
    response = client.get(f"/data/{ACTION}/{INVALID_FILEPATH}")
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Data not found in the provided path"

    INVALID_ACTION = "preload"
    FILEPATH = "dataset-217-version-2/derivative/scaffold_context_info.json"
    response = client.get(f"/data/{INVALID_ACTION}/{FILEPATH}")
    result = response.json()
    assert response.status_code == 422
    # assert response.status_code == 405
    # assert result["detail"] == "The action is not provided in this API"

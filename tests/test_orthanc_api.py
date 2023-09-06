import pytest
from app import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as client:
        return client


def test_get_orthanc_instance(client):
    pass_case = {
        "study": "1.3.6.1.4.1.14519.5.2.1.186051521067863971269584893740842397538",
        "series": "1.3.6.1.4.1.14519.5.2.1.175414966301645518238419021688341658582"
    }
    response = client.post("/instance", json=pass_case)
    result = response.json()
    assert response.status_code == 200
    assert len(result) == 42

    missing_data = {}
    response = client.post("/instance", json=missing_data)
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Missing one or more fields in the request body"

    wrong_data = {
        "study": "fakestudy",
        "series": "fakeseries"
    }
    response = client.post("/instance", json=wrong_data)
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Resource is not found in the orthanc server"


def test_get_orthanc_dicom_file(client):
    IDENTIFIER = "5490c29e-b24b6cf6-8ad2e2af-5056e4b5-e67f118e"
    response = client.get(f"/dicom/export/{IDENTIFIER}")
    assert response.status_code == 200

    INVALID_IDENTIFIER = "fakeuuid"
    response = client.get(f"/dicom/export/{INVALID_IDENTIFIER}")
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Resource is not found in the orthanc server"

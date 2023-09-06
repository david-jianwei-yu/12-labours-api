import pytest
from app import app
from fastapi.testclient import TestClient

from app.config import Gen3Config
from app.filter_generator import FILTERS


@pytest.fixture
def client():
    with TestClient(app) as client:
        return client


def test_create_gen3_access(client):
    missing_data = {}
    response = client.post("/access/token", json=missing_data)
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Missing field in the request body"

    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    result = response.json()
    assert response.status_code == 200
    assert result["identity"] == dummy_data["identity"]


def test_revoke_gen3_access(client):
    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    response = client.delete(
        "/access/revoke", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "Unable to remove default access authority"


def test_get_gen3_dictionary(client):
    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    response = client.post(
        "/dictionary", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    assert response.status_code == 200


def test_get_gen3_record(client):
    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    UUID = "5b9ae1bd-e780-4869-a458-b3422084c480"
    response = client.get(
        f"/record/{UUID}", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 200
    assert len(result) == 1
    assert result["record"]["submitter_id"] == "dataset-217-version-2-dataset_description"

    UUID = "5b9ae1bd-e780-4869-a458-fakeuuidsuffix"
    response = client.get(
        f"/record/{UUID}", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == f"Unable to find {UUID} and check if the correct project or uuid is used"


def test_get_gen3_graphql_query(client):
    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    DATASET_ID = "dataset-217-version-2"
    pass_case = {
        "node": "experiment_query",
        "filter": {
            "submitter_id": [DATASET_ID]
        },
        "search": ""
    }
    response = client.post("/graphql/query", json=pass_case,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 200
    assert result["data"]["submitter_id"] == DATASET_ID
    assert len(result["facets"]) == 2
    assert result["facets"][0] == {
        "facet": "Brainstem",
        "term": "Anatomical structure",
        "facetPropPath": "dataset_description_filter>study_organ_system"
    }

    missing_data = {}
    response = client.post("/graphql/query", json=missing_data,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Missing one or more fields in the request body"

    wrong_node = {
        "node": "fakenode",
    }
    response = client.post("/graphql/query", json=wrong_node,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "GraphQL query cannot be generated by sgqlc"


def test_get_gen3_graphql_pagination(client):
    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    filter_pass_case = {
        "filter": {
            "manifest_filter>additional_types": [
                "Plot"
            ],
            "case_filter>species": [
                "Rat"
            ],
            "case_filter>sex": [
                "Male"
            ]
        }
    }
    response = client.post("/graphql/pagination/", json=filter_pass_case,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 200
    assert result["items"][0]["datasetId"] == "dataset-46-version-2"
    assert result["total"] == 1

    order_pass_case = {
        "order": "Title(desc)"
    }
    response = client.post("/graphql/pagination/?search=", json=order_pass_case,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 200
    assert result["items"][13]["datasetId"] == "dataset-46-version-2"

    search_pass_case = {}
    response = client.post("/graphql/pagination/?search=rats", json=search_pass_case,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 200
    assert result["items"][0]["datasetId"] == "dataset-46-version-2"
    assert result["total"] == 1

    wrong_search = {}
    response = client.post("/graphql/pagination/?search=dog", json=wrong_search,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "There is no matched content in the database"

    wrong_facet = {
        "filter": {
            "manifest_filter>additional_types": [
                "Image"
            ],
        }
    }
    response = client.post("/graphql/pagination/", json=wrong_facet,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Invalid or unauthorized facet passed in"

    wrong_order = {
        "order": "Author(asc)"
    }
    response = client.post("/graphql/pagination/", json=wrong_order,
                           headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == f"{wrong_order['order']} order option not provided"


def test_get_gen3_filter(client):
    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    response = client.get("/filter/?sidebar=true",
                          headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    assert response.status_code == 200
    assert bool(FILTERS["MAPPED_AGE_CATEGORY"]["facets"]) == True
    assert bool(FILTERS["MAPPED_STUDY_ORGAN_SYSTEM"]["facets"]) == True
    assert bool(FILTERS["MAPPED_SEX"]["facets"]) == True
    assert bool(FILTERS["MAPPED_ADDITIONAL_TYPES"]["facets"]) == True
    assert bool(FILTERS["MAPPED_SPECIES"]["facets"]) == True
    assert bool(FILTERS["MAPPED_PROJECT_ID"]["facets"]) == True

    response = client.get("/filter/?sidebar=false",
                          headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    assert response.status_code == 200
    assert bool(FILTERS["MAPPED_AGE_CATEGORY"]["facets"]) == True
    assert bool(FILTERS["MAPPED_STUDY_ORGAN_SYSTEM"]["facets"]) == True
    assert bool(FILTERS["MAPPED_SEX"]["facets"]) == True
    assert bool(FILTERS["MAPPED_ADDITIONAL_TYPES"]["facets"]) == True
    assert bool(FILTERS["MAPPED_SPECIES"]["facets"]) == True
    assert bool(FILTERS["MAPPED_PROJECT_ID"]["facets"]) == True


def test_get_gen3_metadata_file(client):
    dummy_data = {
        "identity": "dummy_email@gmail.com>dummy_machine_id>dummy_expiration_time"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    UUID = "22c4459b-5f4f-4e62-abd2-2aa205fe838b"
    FORM = "json"
    response = client.get(f"/metadata/download/{UUID}/{FORM}",
                          headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 200
    assert len(result) == 18
    assert result["submitter_id"] == "dataset-217-version-2"

    UUID = "22c4459b-5f4f-4e62-abd2-fakeuuidsuffix"
    FORM = "json"
    response = client.get(f"/metadata/download/{UUID}/{FORM}",
                          headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == f"Unable to find {UUID} and check if the correct project or uuid is used"

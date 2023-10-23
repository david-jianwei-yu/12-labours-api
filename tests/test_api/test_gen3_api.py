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


def test_get_gen3_record(client, token):
    UUID = "5b9ae1bd-e780-4869-a458-b3422084c480"
    response = client.get(
        f"/record/{UUID}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert len(result) == 1
    assert (
        result["record"]["submitter_id"] == "dataset-217-version-2-dataset_description"
    )

    UUID = "5b9ae1bd-e780-4869-a458-fakeuuidsuffix"
    response = client.get(
        f"/record/{UUID}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Data does not exist or unable to access the data"


def test_get_gen3_graphql_query(client, token):
    DATASET_ID = "dataset-217-version-2"
    pass_case = {
        "node": "experiment_query",
        "filter": {"submitter_id": [DATASET_ID]},
        "search": "",
    }
    response = client.post(
        "/graphql/query?mode=data",
        json=pass_case,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert result["data"]["submitter_id"] == DATASET_ID

    response = client.post(
        "/graphql/query?mode=detail",
        json=pass_case,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert result["detail"]["submitter_id"] == DATASET_ID
    assert result["facet"] == {
        "Anatomical structure": ["Brainstem"],
        "Data type": ["Scaffold"],
    }

    response = client.post(
        "/graphql/query?mode=facet",
        json=pass_case,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert len(result["facet"]) == 2
    assert result["facet"] == [
        {
            "facet": "Scaffold",
            "term": "Data type",
            "facetPropPath": "manifest_filter>additional_types",
        },
        {
            "facet": "Brainstem",
            "term": "Anatomical structure",
            "facetPropPath": "dataset_description_filter>study_organ_system",
        },
    ]

    missing_data = {}
    response = client.post(
        "/graphql/query?mode=data",
        json=missing_data,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Missing field in the request body"

    wrong_node = {
        "node": "fakenode",
    }
    response = client.post(
        "/graphql/query?mode=data",
        json=wrong_node,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Invalid query node is used"

    invalid_search = {
        "node": "experiment_query",
        "filter": {"submitter_id": [DATASET_ID]},
        "search": "dummy content",
    }
    response = client.post(
        "/graphql/query?mode=data",
        json=invalid_search,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 405
    assert result["detail"] == "Search does not provide in current node"

    DATASET_ID2 = "dataset-46-version-2"
    wrong_filter = {
        "node": "experiment_query",
        "filter": {"submitter_id": [DATASET_ID, DATASET_ID2]},
        "search": "",
    }
    response = client.post(
        "/graphql/query?mode=detail",
        json=wrong_filter,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 400
    assert (
        result["detail"]
        == "Mode detail only available when query one dataset in experiment node"
    )


def test_get_gen3_graphql_pagination(client, token):
    filter_pass_case = {
        "filter": {
            "dataset_description_filter>study_organ_system": ["Stomach", "Vagus nerve"],
            "manifest_filter>additional_types": ["Plot"],
            "case_filter>species": ["Rat"],
            "case_filter>sex": ["Male"],
        }
    }
    response = client.post(
        "/graphql/pagination",
        json=filter_pass_case,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert result["items"][0]["datasetId"] == "dataset-46-version-2"
    assert result["total"] == 1

    order_pass_case = {"order": "Title(desc)"}
    response = client.post(
        "/graphql/pagination?search=",
        json=order_pass_case,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert result["items"][14]["datasetId"] == "dataset-46-version-2"

    search_pass_case = {}
    response = client.post(
        "/graphql/pagination?search=rats",
        json=search_pass_case,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert result["items"][0]["datasetId"] == "dataset-46-version-2"
    assert result["total"] == 1

    wrong_search = {}
    response = client.post(
        "/graphql/pagination?search=dog",
        json=wrong_search,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "There is no matched content in the database"

    wrong_facet = {
        "filter": {
            "manifest_filter>additional_types": ["Image"],
        }
    }
    response = client.post(
        "/graphql/pagination",
        json=wrong_facet,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Invalid or unauthorized facet passed in"

    wrong_order = {"order": "Author(asc)"}
    response = client.post(
        "/graphql/pagination",
        json=wrong_order,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == f"{wrong_order['order']} order option not provided"


def test_get_gen3_filter(client, token):
    response = client.get(
        "/filter?sidebar=true",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert "key" in result[0]
    assert "label" in result[0]
    assert "children" in result[0]
    assert "facetPropPath" in result[0]["children"][0]
    assert "label" in result[0]["children"][0]
    assert len(result) == 6

    response = client.get(
        "/filter?sidebar=false",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()
    assert response.status_code == 200
    assert "size" in result
    assert "titles" in result
    assert "nodes>fields" in result
    assert "elements" in result
    assert result["size"] == 6
    assert result["titles"] == [
        "Data type",
        "Age category",
        "Access scope",
        "Sex",
        "Species",
        "Anatomical structure",
    ]
    assert result["nodes>fields"] == [
        "manifest_filter>additional_types",
        "case_filter>age_category",
        "experiment_filter>project_id",
        "case_filter>sex",
        "case_filter>species",
        "dataset_description_filter>study_organ_system",
    ]

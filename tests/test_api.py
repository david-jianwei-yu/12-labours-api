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
        "email": "dummyemail@gmail.com"
    }
    response = client.post("/access/token", json=dummy_data)
    result = response.json()
    assert response.status_code == 200
    assert result["email"] == dummy_data["email"]


def test_revoke_gen3_access(client):
    dummy_data = {
        "email": "dummyemail@gmail.com"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()
    response = client.delete(
        "/access/revoke", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "Unable to remove default access authority"


def test_get_gen3_access(client):
    dummy_data = {
        "email": "dummyemail@gmail.com"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()
    response = client.get(
        "/access/authorize", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()
    assert response.status_code == 200
    assert len(result) == 1
    assert result["access"][0] == Gen3Config.PUBLIC_ACCESS

    response = client.get(
        "/access/authorize", headers={"Authorization": "Bearer fakeaccesstoken"})
    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "Invalid authentication credentials"


def test_get_gen3_dictionary(client):
    pass_case = {
        "access": [Gen3Config.PUBLIC_ACCESS],
    }
    response = client.post("/dictionary", json=pass_case)
    assert response.status_code == 200

    invalid_data = {
        "access": ["fakeprog-fakeproj"],
    }
    response = client.post("/dictionary", json=invalid_data)
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "Program fakeprog or project fakeproj not found"


def test_get_gen3_node_records(client):
    NODE_TYPE = "experiment"

    pass_case = {
        "access": [Gen3Config.PUBLIC_ACCESS],
    }
    response = client.post(f"/records/{NODE_TYPE}", json=pass_case)
    result = response.json()
    assert response.status_code == 200
    assert "data" in result

    invalid_program = {
        "access": ["fakeprog-12L"],
    }
    response = client.post(f"/records/{NODE_TYPE}", json=invalid_program)
    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "You don't have access to this resource: user is unauthorized"

    invalid_project = {
        "access": ["demo1-fakeproj"],
    }
    response = client.post(f"/records/{NODE_TYPE}", json=invalid_project)
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "No data found with node type experiment and check if the correct project or node type is used"

    NODE_TYPE = "experiments"
    response = client.post(f"/records/{NODE_TYPE}", json=pass_case)
    assert response.status_code == 422


def test_get_gen3_record(client):
    UUID = "5b9ae1bd-e780-4869-a458-b3422084c480"

    pass_case = {
        "access": [Gen3Config.PUBLIC_ACCESS],
    }
    response = client.post(f"/record/{UUID}", json=pass_case)
    result = response.json()
    assert response.status_code == 200
    assert len(result) == 1
    assert result[0]["submitter_id"] == "dataset-217-version-2-dataset_description"

    invalid_program = {
        "access": ["fakeprog-12L"],
    }
    response = client.post(f"/record/{UUID}", json=invalid_program)
    result = response.json()
    assert response.status_code == 401
    assert result["detail"] == "You don't have access to this resource: user is unauthorized"

    invalid_project = {
        "access": ["demo1-fakeproj"],
    }
    response = client.post(f"/record/{UUID}", json=invalid_project)
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == f"Unable to find {UUID} and check if the correct project or uuid is used"


def test_graphql_query(client):
    DATASET_ID = "dataset-217-version-2"
    pass_case = {
        "node": "experiment_query",
        "filter": {
            "submitter_id": [DATASET_ID]
        },
        "search": ""
    }
    response = client.post("/graphql/query", json=pass_case)
    result = response.json()
    assert response.status_code == 200
    assert result[0]["submitter_id"] == DATASET_ID

    missing_data = {}
    response = client.post("/graphql/query", json=missing_data)
    result = response.json()
    assert response.status_code == 400
    assert result["detail"] == "Missing one or more fields in the request body"


def test_graphql_pagination(client):
    filter_pass_case = {
        "filter": {
            "1": {
                "node": "manifest_filter",
                "filter": {
                    "additional_types": [
                        "text/vnd.abi.plot+tab-separated-values",
                        "text/vnd.abi.plot+csv"
                    ]
                }
            },
            "2": {
                "node": "case_filter",
                "filter": {
                        "species": [
                            "Rattus norvegicus"
                        ]
                }
            },
            "3": {
                "node": "case_filter",
                "filter": {
                        "sex": [
                            "Male"
                        ]
                }
            }
        },
        "relation": "and"
    }
    response = client.post("/graphql/pagination/", json=filter_pass_case)
    result = response.json()
    assert response.status_code == 200
    assert result["items"][0]["datasetId"] == "dataset-46-version-2"
    assert result["total"] == 1

    search_pass_case = {
        "filter": {},
        "relation": "and"
    }
    response = client.post(
        "/graphql/pagination/?search=rats", json=search_pass_case)
    result = response.json()
    assert response.status_code == 200
    assert result["items"][0]["datasetId"] == "dataset-46-version-2"
    assert result["total"] == 1

    search_not_found = {
        "filter": {},
        "relation": "and"
    }
    response = client.post(
        "/graphql/pagination/?search=dog", json=search_not_found)
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "There is no matched content in the database"

    pass_case = {
        "filter": {
            "1": {
                "node": "manifest_filter",
                "filter": {
                    "additional_types": [
                        "text/vnd.abi.plot+tab-separated-values",
                        "text/vnd.abi.plot+csv"
                    ]
                }
            },
            "2": {
                "node": "case_filter",
                "filter": {
                        "species": [
                            "Rattus norvegicus"
                        ]
                }
            },
            "3": {
                "node": "case_filter",
                "filter": {
                        "sex": [
                            "Male"
                        ]
                }
            }
        },
        "relation": "and"
    }
    response = client.post("/graphql/pagination/?search=rats", json=pass_case)
    result = response.json()
    assert response.status_code == 200
    assert result["items"][0]["datasetId"] == "dataset-46-version-2"
    assert result["total"] == 1

    wrong_data = {
        "filter": {
            "1": {
                "node": "fakenode_filter",
                "filter": {
                    "additional_types": [
                        "text/vnd.abi.plot+tab-separated-values",
                        "text/vnd.abi.plot+csv"
                    ]
                }
            },
        },
        "relation": "and"
    }
    response = client.post("/graphql/pagination/", json=wrong_data)
    result = response.json()
    assert response.status_code == 404
    assert result["detail"] == "GraphQL query cannot be generated by sgqlc"


def test_get_filter(client):
    pass_case = {
        "access": [Gen3Config.PUBLIC_ACCESS],
    }
    response = client.post("/filter/?sidebar=true", json=pass_case)
    assert response.status_code == 200
    assert bool(FILTERS["MAPPED_AGE_CATEGORY"]["element"]) == True
    assert bool(FILTERS["MAPPED_ANATOMICAL_STRUCTURE"]["element"]) == True
    assert bool(FILTERS["MAPPED_SEX"]["element"]) == True
    assert bool(FILTERS["MAPPED_MIME_TYPE"]["element"]) == True
    assert bool(FILTERS["MAPPED_SPECIES"]["element"]) == True

    response = client.post("/filter/?sidebar=false", json=pass_case)
    assert response.status_code == 200
    assert bool(FILTERS["MAPPED_AGE_CATEGORY"]["element"]) == True
    assert bool(FILTERS["MAPPED_ANATOMICAL_STRUCTURE"]["element"]) == True
    assert bool(FILTERS["MAPPED_SEX"]["element"]) == True
    assert bool(FILTERS["MAPPED_MIME_TYPE"]["element"]) == True
    assert bool(FILTERS["MAPPED_SPECIES"]["element"]) == True


def test_download_gen3_metadata_file(client):
    PROG_NAME = "demo1"
    PROJ_NAME = "12L"
    UUID = "22c4459b-5f4f-4e62-abd2-2aa205fe838b"
    FORM = "json"
    response = client.get(
        f"/metadata/download/{PROG_NAME}/{PROJ_NAME}/{UUID}/{FORM}")
    result = response.json()
    assert response.status_code == 200
    assert len(result) == 18
    assert result["submitter_id"] == "dataset-217-version-2"


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

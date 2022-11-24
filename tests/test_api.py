import pytest
from app import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as client:
        return client


def test_get_gen3_program(client):
    response = client.get("/program")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()["program"][0] == "demo1"


def test_get_gen3_project(client):
    response = client.get("/project/demo1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()["project"][0] == "12L"

    response = client.get("/project/demo")
    assert response.status_code == 422


def test_get_gen3_dictionary(client):
    pass_case = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post("/dictionary", json=pass_case)
    assert response.status_code == 200

    missing_data = {}
    response = client.post("/dictionary", json=missing_data)
    assert response.status_code == 400
    assert response.json()[
        "detail"] == "Missing one or more fields in the request body"

    invalid_data = {
        "program": "demo",
        "project": "12L",
    }
    response = client.post("/dictionary", json=invalid_data)
    assert response.status_code == 404
    assert response.json()[
        "detail"] == "Program demo or project 12L not found"


def test_get_gen3_node_records(client):
    NODE_TYPE = "experiment"

    pass_case = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(f"/records/{NODE_TYPE}", json=pass_case)
    assert response.status_code == 200
    assert "data" in response.json()

    missing_data = {}
    response = client.post(f"/records/{NODE_TYPE}", json=missing_data)
    assert response.status_code == 400
    assert response.json()[
        "detail"] == "Missing one or more fields in the request body"

    invalid_program = {
        "program": "demo",
        "project": "12L",
    }
    response = client.post(f"/records/{NODE_TYPE}", json=invalid_program)
    assert response.status_code == 401
    assert response.json()[
        "detail"] == "You don't have access to this resource: user is unauthorized"

    invalid_project = {
        "program": "demo1",
        "project": "12Labours",
    }
    response = client.post(f"/records/{NODE_TYPE}", json=invalid_project)
    assert response.status_code == 404
    assert response.json()[
        "detail"] == "No data found with node type experiment and check if the correct project or node type is used"

    NODE_TYPE = "experiments"
    response = client.post(f"/records/{NODE_TYPE}", json=pass_case)
    assert response.status_code == 422


def test_get_gen3_record(client):
    UUID = "fcf89c10-20ae-43a9-afb4-a7b107a2b541"

    pass_case = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(f"/record/{UUID}", json=pass_case)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[
        0]["submitter_id"] == "dataset-76-version-7-dataset_description"

    missing_data = {}
    response = client.post(f"/record/{UUID}", json=missing_data)
    assert response.status_code == 400
    assert response.json()[
        "detail"] == "Missing one or more fields in the request body"

    invalid_program = {
        "program": "demo",
        "project": "12L",
    }
    response = client.post(f"/record/{UUID}", json=invalid_program)
    assert response.status_code == 401
    assert response.json()[
        "detail"] == "You don't have access to this resource: user is unauthorized"

    invalid_project = {
        "program": "demo1",
        "project": "12Labours",
    }
    response = client.post(f"/record/{UUID}", json=invalid_project)
    assert response.status_code == 404
    assert response.json()[
        "detail"] == "Unable to find fcf89c10-20ae-43a9-afb4-a7b107a2b541 and check if uses the correct project or uuid is used"


def test_graphql_query(client):
    pass_case = {
        "node": "manifest",
        "filter": {
            "additional_types": ["application/x.vnd.abi.scaffold.meta+json"],
        },
        "search": "",
    }
    response = client.post("/graphql", json=pass_case)
    assert response.status_code == 200
    assert "data" in response.json()

    missing_data = {}
    response = client.post("/graphql", json=missing_data)
    assert response.status_code == 400
    assert response.json()[
        "detail"] == "Missing one or more fields in the request body"

    wrong_data = {
        "node": "irods",
        "filter": {
            "additional_types": ["application/x.vnd.abi.scaffold.meta+json"],
        },
        "search": "",
    }
    response = client.post("/graphql", json=wrong_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Query cannot be generated"


def test_generate_filters(client):
    pass_case = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post("/filters", json=pass_case)
    assert response.status_code == 200

    invalid_program = {
        "program": "demo",
        "project": "12L",
    }
    response = client.post("/filters", json=invalid_program)
    assert response.status_code == 401
    assert response.json()[
        "detail"] == "You don't have access to this resource: user is unauthorized"

    invalid_project = {
        "program": "demo1",
        "project": "12Labours",
    }
    response = client.post("/filters", json=invalid_project)
    assert response.status_code == 404
    assert response.json()[
        "detail"] == "No data found with node type manifest and check if the correct project or node type is used"


def test_download_gen3_metadata_file(client):
    PROG_NAME = "demo1"
    PROJ_NAME = "12L"
    UUID = "fcf89c10-20ae-43a9-afb4-a7b107a2b541"
    FORM = "json"
    response = client.get(
        f"/metadata/download/{PROG_NAME}/{PROJ_NAME}/{UUID}/{FORM}")
    assert response.status_code == 200
    assert len(response.json()) == 29
    assert response.json()[
        "submitter_id"] == "dataset-76-version-7-dataset_description"


def test_get_irods_root_collections(client):
    response = client.get("/collection")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_irods_collections(client):
    pass_case = {
        "path": "/tempZone/home/rods/datasets"
    }
    response = client.post("/collection", json=pass_case)
    assert response.status_code == 200
    assert len(response.json()) == 2

    missing_data = {}
    response = client.post("/collection", json=missing_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing field in request body"

    wrong_path = {
        "path": "/tempZone/home/rods/data"
    }
    response = client.post("/collection", json=wrong_path)
    assert response.status_code == 404
    assert response.json()["detail"] == "Wrong dataset file path passed"


def test_get_irods_data_file(client):
    ACTION = "preview"
    FILEPATH = "datasets/dataset-217-version-2/derivative/scaffold_context_info.json"
    response = client.get(f"/data/{ACTION}/{FILEPATH}")
    assert response.status_code == 200
    assert response.json() == {"description": "Annotated brainstem scaffold for pig available for registration of segmented neural anatomical-functional mapping of neural circuits.",
                               "heading": "Generic pig brainstem scaffold", "id": "sparc.science.context_data", "samples": [], "version": "0.1.0", "views": []}

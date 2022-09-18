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
    assert response.json() == {"program": ["demo1"]}


def test_get_gen3_project(client):
    response = client.get("/project/demo1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json() == {"project": ["12L"]}


def test_get_gen3_dictionary(client):
    response = client.get("/dictionary")
    assert response.status_code == 200


def test_get_gen3_node_records(client):
    NODE_TYPE = "experiment"

    test_data_pass = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(f"/records/{NODE_TYPE}", json=test_data_pass)
    assert response.status_code == 200
    assert "data" in response.json()

    test_data_failed_400 = {}
    response = client.post(f"/records/{NODE_TYPE}", json=test_data_failed_400)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Missing one ore more fields in request body."}

    test_data_failed_403 = {
        "program": "demo",
        "project": "12L",
    }
    response = client.post(f"/records/{NODE_TYPE}", json=test_data_failed_403)
    assert response.status_code == 403

    # test_data_failed_404 = {
    #     "program": "demo1",
    #     "project": "12Labours",
    #     "format": "json",
    # }
    # response = client.post(f"/records/{NODE_TYPE}", json=test_data_failed_404)
    # assert response.status_code == 404


def test_get_gen3_record(client):
    UUID = "fcf89c10-20ae-43a9-afb4-a7b107a2b541"

    test_data_pass = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(f"/record/{UUID}", json=test_data_pass)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[
        0]["submitter_id"] == "dataset-76-version-7-dataset_description"

    test_data_failed_400 = {}
    response = client.post(f"/record/{UUID}", json=test_data_failed_400)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Missing one ore more fields in request body."}

    test_data_failed_403 = {
        "program": "demo",
        "project": "12L",
    }
    response = client.post(f"/record/{UUID}", json=test_data_failed_403)
    assert response.status_code == 403


def test_graphql_query(client):
    test_data_pass = {
        "limit": 10,
        "page": 1,
        "node": "manifest",
        "filter": {
            "additional_types": ["application/x.vnd.abi.scaffold.meta+json"],
        },
        "search": "",
    }
    response = client.post("/graphql", json=test_data_pass)
    assert response.status_code == 200
    assert "data" in response.json()

    test_data_failed_400 = {}
    response = client.post("/graphql", json=test_data_failed_400)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Missing one ore more fields in request body."}

    test_data_failed_404 = {
        "limit": 10,
        "page": 1,
        "node": "irods",
        "filter": {
            "additional_types": ["application/x.vnd.abi.scaffold.meta+json"],
        },
        "search": "",
    }
    response = client.post("/graphql", json=test_data_failed_404)
    assert response.status_code == 404


def test_generate_filters(client):
    test_data_pass = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post("/filters", json=test_data_pass)
    assert response.status_code == 200

    test_data_failed_403 = {
        "program": "demo",
        "project": "12L",
    }
    response = client.post("/filters", json=test_data_failed_403)
    assert response.status_code == 403


def test_download_gen3_metadata_file(client):
    PROG_NAME = "demo1"
    PROJ_NAME = "12L"
    UUID = "fcf89c10-20ae-43a9-afb4-a7b107a2b541"
    FORM = "json"
    response = client.get(
        f"/download/metadata/{PROG_NAME}/{PROJ_NAME}/{UUID}/{FORM}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[
        0]["submitter_id"] == "dataset-76-version-7-dataset_description"


def test_get_irods_root_collections(client):
    response = client.get("/collection")
    assert response.status_code == 200


def test_get_irodst_collections(client):
    test_post_data_pass = {
        "path": "/tempZone/home/rods/datasets"
    }
    response = client.post("/collection", json=test_post_data_pass)
    assert response.status_code == 200

    test_post_data_failed_400 = {}
    response = client.post("/collection", json=test_post_data_failed_400)
    assert response.status_code == 400
    assert response.json() == {"detail": "Missing field in request body."}

    test_post_data_failed_404 = {
        "path": "/tempZone/home/rods/data"
    }
    response = client.post("/collection", json=test_post_data_failed_404)
    assert response.status_code == 404


def test_preview_irods_data_file(client):
    FILEPATH = "datasets/dataset-217-version-2/derivative/scaffold_context_info.json"
    response = client.get(f"/preview/data/{FILEPATH}")
    assert response.status_code == 200
    assert response.json() == {"description": "Annotated brainstem scaffold for pig available for registration of segmented neural anatomical-functional mapping of neural circuits.",
                               "heading": "Generic pig brainstem scaffold", "id": "sparc.science.context_data", "samples": [], "version": "0.1.0", "views": []}


def test_download_irods_data_file(client):
    FILEPATH = "datasets/dataset-217-version-2/derivative/scaffold_context_info.json"
    response = client.get(f"/download/data/{FILEPATH}")
    assert response.status_code == 200
    assert response.json() == {"description": "Annotated brainstem scaffold for pig available for registration of segmented neural anatomical-functional mapping of neural circuits.",
                               "heading": "Generic pig brainstem scaffold", "id": "sparc.science.context_data", "samples": [], "version": "0.1.0", "views": []}

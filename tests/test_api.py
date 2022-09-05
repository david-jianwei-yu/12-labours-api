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
    assert len(response.json()["dictionary"]) == 20
    assert response.json() == {"dictionary": ["root", "data_release", "slide_count", "case", "resource", "code_description", "performance", "experiment", "program", "experimental_metadata",
                                              "core_metadata_collection", "project", "code_parameter", "slide", "dataset_description", "submission", "sample", "slide_image", "aliquot", "_all"]}


def test_get_gen3_node_records(client):
    NODE_TYPE = "slide"

    test_data_pass = {
        "program": "demo1",
        "project": "12L",
        "format": "json",
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
        "format": "json",
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
    UUID = "ccc2e137-acc4-4703-9954-be61fa4b638a"

    test_data_pass = {
        "program": "demo1",
        "project": "12L",
        "format": "json",
    }
    response = client.post(f"/record/{UUID}", json=test_data_pass)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[
        0]["submitter_id"] == "dataset-217-version-2-derivative-scaffold_context_info-json"

    test_data_failed_400 = {}
    response = client.post(f"/record/{UUID}", json=test_data_failed_400)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Missing one ore more fields in request body."}

    test_data_failed_403 = {
        "program": "demo",
        "project": "12L",
        "format": "json",
    }
    response = client.post(f"/record/{UUID}", json=test_data_failed_403)
    assert response.status_code == 403

    test_data_failed_404 = {
        "program": "demo1",
        "project": "12Labours",
        "format": "json",
    }
    response = client.post(f"/record/{UUID}", json=test_data_failed_404)
    assert response.status_code == 404


def test_graphql_query(client):
    test_data_pass = {
        "node": "slide",
        "filter": {
            "file_type": ["jpeg", ".xlsx", ".txt"],
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
        "node": "slides",
        "filter": {
            "file_type": ["jpeg", ".xlsx", ".txt"],
        },
        "search": "",
    }
    response = client.post("/graphql", json=test_data_failed_404)
    assert response.status_code == 404


def test_download_gen3_metadata_file(client):
    PROG_NAME = "demo1"
    PROJ_NAME = "12L"
    UUID = "ccc2e137-acc4-4703-9954-be61fa4b638a"
    FORM = "json"
    NAME = "testname"
    response = client.get(
        f"/download/metadata/{PROG_NAME}/{PROJ_NAME}/{UUID}/{FORM}/{NAME}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[
        0]["submitter_id"] == "dataset-217-version-2-derivative-scaffold_context_info-json"


def test_get_irods_root_collections(client):
    response = client.get("/collection")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json() == {'files': [], 'folders': [{'id': 10014, 'name': 'datasets', 'path': '/tempZone/home/rods/datasets'}, {
        'id': 10068, 'name': 'uploads', 'path': '/tempZone/home/rods/uploads'}]}


def test_get_irodst_collections(client):
    test_post_data_pass = {
        "path": "/tempZone/home/rods/datasets"
    }
    response = client.post("/collection", json=test_post_data_pass)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json() == {'files': [], 'folders': [{'id': 10030, 'name': 'dataset-217-version-2', 'path': '/tempZone/home/rods/datasets/dataset-217-version-2'}, {'id': 10031, 'name': 'dataset-264-version-1', 'path': '/tempZone/home/rods/datasets/dataset-264-version-1'}]} != {
        'folders': [{'id': 10030, 'name': 'dataset-217-version-2', 'path': '/tempZone/home/rods/datasets/dataset...ion-2'}, {'id': 10031, 'name': 'dataset-264-version-1', 'path': '/tempZone/home/rods/datasets/dataset-264-version-1'}]}

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
    SUFFIX = "datasets&dataset-217-version-2&derivative&scaffold_context_info.json"
    response = client.get(f"/preview/data/{SUFFIX}")
    assert response.status_code == 200
    assert response.json() == {"description": "Annotated brainstem scaffold for pig available for registration of segmented neural anatomical-functional mapping of neural circuits.",
                               "heading": "Generic pig brainstem scaffold", "id": "sparc.science.context_data", "samples": [], "version": "0.1.0", "views": []}


def test_download_irods_data_file(client):
    SUFFIX = "datasets&dataset-217-version-2&derivative&scaffold_context_info.json"
    response = client.get(f"/download/data/{SUFFIX}")
    assert response.status_code == 200
    assert response.json() == {"description": "Annotated brainstem scaffold for pig available for registration of segmented neural anatomical-functional mapping of neural circuits.",
                               "heading": "Generic pig brainstem scaffold", "id": "sparc.science.context_data", "samples": [], "version": "0.1.0", "views": []}

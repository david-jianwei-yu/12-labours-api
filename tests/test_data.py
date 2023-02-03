import pytest
from app import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as client:
        return client


# Database and Search Engine Knowledge Testing
# Test the original data against the data coming out from the backend api search/filter api to make sure the information is correct and up-to-date
# Focus on Data Structure and Format
# Testing will based on ->//# dataset-217-version-2 #//<-
def test_experiment_node(client):
    UUID = "22c4459b-5f4f-4e62-abd2-2aa205fe838b"
    payload = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(
        f"/record/{UUID}", json=payload)
    result = response.json()

    assert result[0]["id"] == UUID
    assert type(result[0]["id"]) is str

    assert result[0]["projects"][0] == {
        "node_id": "ce3985ad-1599-52df-bf54-5f34a87e0120",
        "code": "12L"
    }
    assert type(result[0]["projects"][0]) is dict

    assert result[0]["type"] == "experiment"
    assert type(result[0]["type"]) is str

    assert result[0]["project_id"] == "demo1-12L"
    assert type(result[0]["project_id"]) is str

    assert result[0]["submitter_id"] == "dataset-217-version-2"
    assert type(result[0]["submitter_id"]) is str

    # "associated_experiment": null,
    # "copy_numbers_identified": null,
    # "data_description": null,
    # "experimental_description": null,
    # "experimental_intent": null,
    # "indels_identified": null,
    # "marker_panel_description": null,
    # "number_experimental_group": null,
    # "number_samples_per_experimental_group": null,
    # "somatic_mutations_identified": null,
    # "type_of_data": null,
    # "type_of_sample": null,
    # "type_of_specimen": null


def test_dataset_description_node(client):
    UUID = "5b9ae1bd-e780-4869-a458-b3422084c480"
    payload = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(
        f"/record/{UUID}", json=payload)
    result = response.json()

    assert result[0]["id"] == UUID
    assert type(result[0]["id"]) is str

    assert result[0]["experiments"][0] == {
        "node_id": "22c4459b-5f4f-4e62-abd2-2aa205fe838b",
        "submitter_id": "dataset-217-version-2"
    }
    assert type(result[0]["experiments"][0]) is dict

    assert result[0]["type"] == "dataset_description"
    assert type(result[0]["type"]) is str

    assert result[0]["project_id"] == "demo1-12L"
    assert type(result[0]["project_id"]) is str

    assert result[0]["submitter_id"] == "dataset-217-version-2-dataset_description"
    assert type(result[0]["submitter_id"]) is str

    assert result[0]["contributor_affiliation"] == [
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute"
    ]
    assert type(result[0]["contributor_affiliation"]) is list

    assert result[0]["contributor_affiliation"] == [
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute"
    ]
    assert type(result[0]["contributor_affiliation"]) is list

    assert result[0]["contributor_name"] == [
        "Sukasem, Atchariya",
        "Christie, Richard",
        "Hunter, Peter"
    ]
    assert type(result[0]["contributor_name"]) is list

    assert result[0]["contributor_orcid"] == [
        "0000-0002-9749-0557",
        "0000-0003-4336-4640",
        "0000-0001-9665-4145"
    ]
    assert type(result[0]["contributor_orcid"]) is list

    assert result[0]["contributor_role"] == [
        "Researcher",
        "Researcher",
        "Principle Investigator"
    ]
    assert type(result[0]["contributor_role"]) is list

    assert result[0]["keywords"] == [
        "brainstem",
        "pig"
    ]
    assert type(result[0]["keywords"]) is list

    assert result[0]["metadata_version"] == ["1.2.3"]
    assert type(result[0]["metadata_version"]) is list

    assert result[0]["subtitle"] == [
        "Annotated pig brainstem scaffold available for registration of segmented neural anatomical-functional mapping of neural circuits."]
    assert type(result[0]["subtitle"]) is list

    assert result[0]["title"] == ["Generic pig brainstem scaffold"]
    assert type(result[0]["title"]) is list

    assert result[0]["acknowledgments"] == [
        "Beckman Institute for Advanced Science and Technology, Pig Imaging Group, University Of Illiois urbana-champaign"]
    assert type(result[0]["acknowledgments"]) is list

    assert result[0]["funding"] == [
        "OT3OD025349"
    ]
    assert type(result[0]["funding"]) is list

    # "dataset_type": "NA",
    # "identifier": "NA",
    # "identifier_description": "NA",
    # "identifier_type": "NA",
    # "number_of_samples": 0,
    # "number_of_subjects": 0,
    # "relation_type": "NA",
    # "study_approach": "NA",
    # "study_data_collection": "NA",
    # "study_organ_system": [],
    # "study_primary_conclusion": "NA",
    # "study_purpose": "NA",
    # "study_technique": "NA",
    # "study_collection_title": null


def test_manifest_node(client):
    UUID = "fd65a93f-ff62-45e4-b7b6-96419ef4f749"
    payload = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(
        f"/record/{UUID}", json=payload)
    result = response.json()

    assert result[0]["id"] == UUID
    assert type(result[0]["id"]) is str

    assert result[0]["experiments"][0] == {
        "node_id": "22c4459b-5f4f-4e62-abd2-2aa205fe838b",
        "submitter_id": "dataset-217-version-2"
    }
    assert type(result[0]["experiments"][0]) is dict

    assert result[0]["type"] == "manifest"
    assert type(result[0]["type"]) is str

    assert result[0]["project_id"] == "demo1-12L"
    assert type(result[0]["project_id"]) is str

    assert result[0]["submitter_id"] == "dataset-217-version-2-manifest-derivative-pig-brainstem-Layout1-view.json"
    assert type(result[0]["submitter_id"]) is str

    assert result[0]["filename"] == "derivative/pig_brainstem_Layout1_view.json"
    assert type(result[0]["filename"]) is str

    assert result[0]["additional_types"] == "application/x.vnd.abi.scaffold.view+json"
    assert type(result[0]["additional_types"]) is str

    assert result[0]["is_derived_from"] == "pig_brainstem_metadata.json"
    assert type(result[0]["is_derived_from"]) is str

    assert result[0]["is_source_of"] == "pig_brainstem_Layout1_thumbnail.jpeg"
    assert type(result[0]["is_source_of"]) is str

    # "description": "NA",
    # "file_type": "NA",
    # "timestamp": "NA",
    # "additional_metadata": null,
    # "is_described_by": null,
    # "supplemental_json_metadata": null


# Dataset-217-version-2 does not have any file in case node
# Using ->//# dataset-46-version-2 #//<- instead
def test_case_node(client):
    UUID = "c58ab983-6cf9-4174-a7a9-20cdf1d6bc33"
    payload = {
        "program": "demo1",
        "project": "12L",
    }
    response = client.post(
        f"/record/{UUID}", json=payload)
    result = response.json()

    assert result[0]["id"] == UUID
    assert type(result[0]["id"]) is str

    assert result[0]["experiments"][0] == {
        "node_id": "f7bc3db5-4d4c-4c50-9124-0434a66a51a2",
        "submitter_id": "dataset-46-version-2"
    }
    assert type(result[0]["experiments"][0]) is dict

    assert result[0]["type"] == "case"
    assert type(result[0]["type"]) is str

    assert result[0]["project_id"] == "demo1-12L"
    assert type(result[0]["project_id"]) is str

    assert result[0]["submitter_id"] == "dataset-46-version-2-subjects-sub-11011"
    assert type(result[0]["submitter_id"]) is str

    assert result[0]["age"] == "12 weeks"
    assert type(result[0]["age"]) is str

    assert result[0]["pool_id"] == "pool-1"
    assert type(result[0]["pool_id"]) is str

    assert result[0]["rrid_for_strain"] == "RRID:RGD_737903"
    assert type(result[0]["rrid_for_strain"]) is str

    assert result[0]["sex"] == "Male"
    assert type(result[0]["sex"]) is str

    assert result[0]["species"] == "Rattus norvegicus"
    assert type(result[0]["species"]) is str

    assert result[0]["strain"] == "Sprague-Dawley"
    assert type(result[0]["strain"]) is str

    assert result[0]["subject_id"] == "sub-11011"
    assert type(result[0]["subject_id"]) is str

    # "age_category": "NA",
    # "also_in_dataset": "NA",
    # "subject_experimental_group": "NA",
    # "age_range_max": null,
    # "age_range_min": null,
    # "date_of_birth": null,
    # "disease_model": null,
    # "disease_or_disorder": null,
    # "experiment_date": null,
    # "experimental_log_file_path": null,
    # "genotype": null,
    # "handedness": null,
    # "intervention": null,
    # "laboratory_internal_id": null,
    # "phenotype": null,
    # "protocol_title": null,
    # "protocol_url_or_doi": null,
    # "reference_atlas": null


def test_irods_collections(client):
    payload1 = {
        "path": "/tempZone/home/rods/12L/datasets/dataset-217-version-2"
    }
    response = client.post("/collection", json=payload1)
    result = response.json()
    assert result["folders"] == [
        {
            "name": "derivative",
            "path": "/tempZone/home/rods/12L/datasets/dataset-217-version-2/derivative"
        },
        {
            "name": "primary",
            "path": "/tempZone/home/rods/12L/datasets/dataset-217-version-2/primary"
        }
    ]
    assert result["files"] == [
        {
            "name": "dataset_description_gen3.json",
            "path": "/tempZone/home/rods/12L/datasets/dataset-217-version-2/dataset_description_gen3.json"
        },
        {
            "name": "dataset_description.xlsx",
            "path": "/tempZone/home/rods/12L/datasets/dataset-217-version-2/dataset_description.xlsx"
        },
        {
            "name": "manifest_gen3.json",
            "path": "/tempZone/home/rods/12L/datasets/dataset-217-version-2/manifest_gen3.json"
        }
    ]

    payload2 = {
        "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2"
    }
    response = client.post("/collection", json=payload2)
    result = response.json()
    assert result["folders"] == [
        {
            "name": "derivative",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/derivative"
        },
        {
            "name": "docs",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/docs"
        },
        {
            "name": "primary",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/primary"
        },
        {
            "name": "source",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/source"
        }
    ]
    assert result["files"] == [
        {
            "name": "dataset_description.json",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/dataset_description.json"
        },
        {
            "name": "dataset_description.xlsx",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/dataset_description.xlsx"
        },
        {
            "name": "experiment.json",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/experiment.json"
        },
        {
            "name": "manifest_gen3.json",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/manifest_gen3.json"
        },
        {
            "name": "manifest.xlsx",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/manifest.xlsx"
        },
        {
            "name": "subjects.json",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/subjects.json"
        },
        {
            "name": "subjects.xlsx",
            "path": "/tempZone/home/rods/12L/datasets/dataset-46-version-2/subjects.xlsx"
        }
    ]

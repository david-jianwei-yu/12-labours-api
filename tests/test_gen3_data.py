import pytest
from app import app
from fastapi.testclient import TestClient

from app.config import Gen3Config


@pytest.fixture
def client():
    with TestClient(app) as client:
        return client


# Database and Search Engine Knowledge Testing
# Test the original data against the data coming out from the backend api search/filter api to make sure the information is correct and up-to-date
# Focus on Data Structure and Format
# Testing will based on ->//# dataset-217-version-2 #//<-
def test_experiment_node(client):
    dummy_data = {
        "identity": "dummyemail@gmail.com>machine_id"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    UUID = "22c4459b-5f4f-4e62-abd2-2aa205fe838b"
    response = client.get(
        f"/record/{UUID}", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()

    assert result["record"]["id"] == UUID
    assert type(result["record"]["id"]) is str

    assert result["record"]["projects"][0] == {
        "node_id": "ce3985ad-1599-52df-bf54-5f34a87e0120",
        "code": "12L"
    }
    assert type(result["record"]["projects"][0]) is dict

    assert result["record"]["type"] == "experiment"
    assert type(result["record"]["type"]) is str

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert type(result["record"]["project_id"]) is str

    assert result["record"]["submitter_id"] == "dataset-217-version-2"
    assert type(result["record"]["submitter_id"]) is str

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
    dummy_data = {
        "identity": "dummyemail@gmail.com>machine_id"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    UUID = "5b9ae1bd-e780-4869-a458-b3422084c480"
    response = client.get(
        f"/record/{UUID}", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()

    assert result["record"]["id"] == UUID
    assert type(result["record"]["id"]) is str

    assert result["record"]["experiments"][0] == {
        "node_id": "22c4459b-5f4f-4e62-abd2-2aa205fe838b",
        "submitter_id": "dataset-217-version-2"
    }
    assert type(result["record"]["experiments"][0]) is dict

    assert result["record"]["type"] == "dataset_description"
    assert type(result["record"]["type"]) is str

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert type(result["record"]["project_id"]) is str

    assert result["record"]["submitter_id"] == "dataset-217-version-2-dataset_description"
    assert type(result["record"]["submitter_id"]) is str

    assert result["record"]["contributor_affiliation"] == [
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute"
    ]
    assert type(result["record"]["contributor_affiliation"]) is list

    assert result["record"]["contributor_affiliation"] == [
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute"
    ]
    assert type(result["record"]["contributor_affiliation"]) is list

    assert result["record"]["contributor_name"] == [
        "Sukasem, Atchariya",
        "Christie, Richard",
        "Hunter, Peter"
    ]
    assert type(result["record"]["contributor_name"]) is list

    assert result["record"]["contributor_orcid"] == [
        "0000-0002-9749-0557",
        "0000-0003-4336-4640",
        "0000-0001-9665-4145"
    ]
    assert type(result["record"]["contributor_orcid"]) is list

    assert result["record"]["contributor_role"] == [
        "Researcher",
        "Researcher",
        "Principle Investigator"
    ]
    assert type(result["record"]["contributor_role"]) is list

    assert result["record"]["keywords"] == [
        "brainstem",
        "pig"
    ]
    assert type(result["record"]["keywords"]) is list

    assert result["record"]["metadata_version"] == ["1.2.3"]
    assert type(result["record"]["metadata_version"]) is list

    assert result["record"]["subtitle"] == [
        "Annotated pig brainstem scaffold available for registration of segmented neural anatomical-functional mapping of neural circuits."]
    assert type(result["record"]["subtitle"]) is list

    assert result["record"]["title"] == ["Generic pig brainstem scaffold"]
    assert type(result["record"]["title"]) is list

    assert result["record"]["acknowledgments"] == [
        "Beckman Institute for Advanced Science and Technology, Pig Imaging Group, University Of Illiois urbana-champaign"]
    assert type(result["record"]["acknowledgments"]) is list

    assert result["record"]["funding"] == [
        "OT3OD025349"
    ]
    assert type(result["record"]["funding"]) is list

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
    dummy_data = {
        "identity": "dummyemail@gmail.com>machine_id"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    UUID = "fd65a93f-ff62-45e4-b7b6-96419ef4f749"
    response = client.get(
        f"/record/{UUID}", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()

    assert result["record"]["id"] == UUID
    assert type(result["record"]["id"]) is str

    assert result["record"]["experiments"][0] == {
        "node_id": "22c4459b-5f4f-4e62-abd2-2aa205fe838b",
        "submitter_id": "dataset-217-version-2"
    }
    assert type(result["record"]["experiments"][0]) is dict

    assert result["record"]["type"] == "manifest"
    assert type(result["record"]["type"]) is str

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert type(result["record"]["project_id"]) is str

    assert result["record"]["submitter_id"] == "dataset-217-version-2-manifest-derivative-pig-brainstem-Layout1-view.json"
    assert type(result["record"]["submitter_id"]) is str

    assert result["record"]["filename"] == "derivative/pig_brainstem_Layout1_view.json"
    assert type(result["record"]["filename"]) is str

    assert result["record"]["additional_types"] == "application/x.vnd.abi.scaffold.view+json"
    assert type(result["record"]["additional_types"]) is str

    assert result["record"]["is_derived_from"] == "pig_brainstem_metadata.json"
    assert type(result["record"]["is_derived_from"]) is str

    assert result["record"]["is_source_of"] == "pig_brainstem_Layout1_thumbnail.jpeg"
    assert type(result["record"]["is_source_of"]) is str

    # "description": "NA",
    # "file_type": "NA",
    # "timestamp": "NA",
    # "additional_metadata": null,
    # "is_described_by": null,
    # "supplemental_json_metadata": null


# Dataset-217-version-2 does not have any file in case node
# Using ->//# dataset-46-version-2 #//<- instead
def test_case_node(client):
    dummy_data = {
        "identity": "dummyemail@gmail.com>machine_id"
    }
    response = client.post("/access/token", json=dummy_data)
    dummy_token = response.json()

    UUID = "c58ab983-6cf9-4174-a7a9-20cdf1d6bc33"
    response = client.get(
        f"/record/{UUID}", headers={"Authorization": f"Bearer {dummy_token['access_token']}"})
    result = response.json()

    assert result["record"]["id"] == UUID
    assert type(result["record"]["id"]) is str

    assert result["record"]["experiments"][0] == {
        "node_id": "f7bc3db5-4d4c-4c50-9124-0434a66a51a2",
        "submitter_id": "dataset-46-version-2"
    }
    assert type(result["record"]["experiments"][0]) is dict

    assert result["record"]["type"] == "case"
    assert type(result["record"]["type"]) is str

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert type(result["record"]["project_id"]) is str

    assert result["record"]["submitter_id"] == "dataset-46-version-2-subjects-sub-11011"
    assert type(result["record"]["submitter_id"]) is str

    assert result["record"]["age"] == "12 weeks"
    assert type(result["record"]["age"]) is str

    assert result["record"]["pool_id"] == "pool-1"
    assert type(result["record"]["pool_id"]) is str

    assert result["record"]["rrid_for_strain"] == "RRID:RGD_737903"
    assert type(result["record"]["rrid_for_strain"]) is str

    assert result["record"]["sex"] == "Male"
    assert type(result["record"]["sex"]) is str

    assert result["record"]["species"] == "Rattus norvegicus"
    assert type(result["record"]["species"]) is str

    assert result["record"]["strain"] == "Sprague-Dawley"
    assert type(result["record"]["strain"]) is str

    assert result["record"]["subject_id"] == "sub-11011"
    assert type(result["record"]["subject_id"]) is str

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

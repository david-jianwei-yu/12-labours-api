import pytest
from fastapi.testclient import TestClient

from app.config import Gen3Config
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


# Database and Search Engine Knowledge Testing
# Test the original data against the data coming out from the backend api search/filter api to make sure the information is correct and up-to-date
# Focus on Data Structure and Format
# Testing will based on ->//# dataset-217-version-2 #//<-
def test_experiment_node(client, token):
    UUID = "22c4459b-5f4f-4e62-abd2-2aa205fe838b"
    response = client.get(
        f"/record/{UUID}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()

    assert result["record"]["id"] == UUID
    assert isinstance(result["record"]["id"], str)

    assert result["record"]["projects"][0] == {
        "node_id": "ce3985ad-1599-52df-bf54-5f34a87e0120",
        "code": "12L",
    }
    assert isinstance(result["record"]["projects"][0], dict)

    assert result["record"]["type"] == "experiment"
    assert isinstance(result["record"]["type"], str)

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert isinstance(result["record"]["project_id"], str)

    assert result["record"]["submitter_id"] == "dataset-217-version-2"
    assert isinstance(result["record"]["submitter_id"], str)

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


def test_dataset_description_node(client, token):
    UUID = "5b9ae1bd-e780-4869-a458-b3422084c480"
    response = client.get(
        f"/record/{UUID}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()

    assert result["record"]["id"] == UUID
    assert isinstance(result["record"]["id"], str)

    assert result["record"]["experiments"][0] == {
        "node_id": "22c4459b-5f4f-4e62-abd2-2aa205fe838b",
        "submitter_id": "dataset-217-version-2",
    }
    assert isinstance(result["record"]["experiments"][0], dict)

    assert result["record"]["type"] == "dataset_description"
    assert isinstance(result["record"]["type"], str)

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert isinstance(result["record"]["project_id"], str)

    assert (
        result["record"]["submitter_id"] == "dataset-217-version-2-dataset_description"
    )
    assert isinstance(result["record"]["submitter_id"], str)

    assert result["record"]["contributor_affiliation"] == [
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
    ]
    assert isinstance(result["record"]["contributor_affiliation"], list)

    assert result["record"]["contributor_affiliation"] == [
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
        "Auckland Bioegineering Institute",
    ]
    assert isinstance(result["record"]["contributor_affiliation"], list)

    assert result["record"]["contributor_name"] == [
        "Sukasem, Atchariya",
        "Christie, Richard",
        "Hunter, Peter",
    ]
    assert isinstance(result["record"]["contributor_name"], list)

    assert result["record"]["contributor_orcid"] == [
        "0000-0002-9749-0557",
        "0000-0003-4336-4640",
        "0000-0001-9665-4145",
    ]
    assert isinstance(result["record"]["contributor_orcid"], list)

    assert result["record"]["contributor_role"] == [
        "Researcher",
        "Researcher",
        "Principle Investigator",
    ]
    assert isinstance(result["record"]["contributor_role"], list)

    assert result["record"]["keywords"] == ["brainstem", "pig"]
    assert isinstance(result["record"]["keywords"], list)

    assert result["record"]["metadata_version"] == ["1.2.3"]
    assert isinstance(result["record"]["metadata_version"], list)

    assert result["record"]["subtitle"] == [
        "Annotated pig brainstem scaffold available for registration of segmented neural anatomical-functional mapping of neural circuits."
    ]
    assert isinstance(result["record"]["subtitle"], list)

    assert result["record"]["title"] == ["Generic pig brainstem scaffold"]
    assert isinstance(result["record"]["title"], list)

    assert result["record"]["acknowledgments"] == [
        "Beckman Institute for Advanced Science and Technology, Pig Imaging Group, University Of Illiois urbana-champaign"
    ]
    assert isinstance(result["record"]["acknowledgments"], list)

    assert result["record"]["funding"] == ["OT3OD025349"]
    assert isinstance(result["record"]["funding"], list)

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


def test_manifest_node(client, token):
    UUID = "fd65a93f-ff62-45e4-b7b6-96419ef4f749"
    response = client.get(
        f"/record/{UUID}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()

    assert result["record"]["id"] == UUID
    assert isinstance(result["record"]["id"], str)

    assert result["record"]["experiments"][0] == {
        "node_id": "22c4459b-5f4f-4e62-abd2-2aa205fe838b",
        "submitter_id": "dataset-217-version-2",
    }
    assert isinstance(result["record"]["experiments"][0], dict)

    assert result["record"]["type"] == "manifest"
    assert isinstance(result["record"]["type"], str)

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert isinstance(result["record"]["project_id"], str)

    assert (
        result["record"]["submitter_id"]
        == "dataset-217-version-2-manifest-derivative-pig-brainstem-Layout1-view.json"
    )
    assert isinstance(result["record"]["submitter_id"], str)

    assert result["record"]["filename"] == "derivative/pig_brainstem_Layout1_view.json"
    assert isinstance(result["record"]["filename"], str)

    assert (
        result["record"]["additional_types"]
        == "application/x.vnd.abi.scaffold.view+json"
    )
    assert isinstance(result["record"]["additional_types"], str)

    assert result["record"]["is_derived_from"] == "pig_brainstem_metadata.json"
    assert isinstance(result["record"]["is_derived_from"], str)

    assert result["record"]["is_source_of"] == "pig_brainstem_Layout1_thumbnail.jpeg"
    assert isinstance(result["record"]["is_source_of"], str)

    # "description": "NA",
    # "file_type": "NA",
    # "timestamp": "NA",
    # "additional_metadata": null,
    # "is_described_by": null,
    # "supplemental_json_metadata": null


# Dataset-217-version-2 does not have any file in case node
# Using ->//# dataset-46-version-2 #//<- instead
def test_case_node(client, token):
    UUID = "c58ab983-6cf9-4174-a7a9-20cdf1d6bc33"
    response = client.get(
        f"/record/{UUID}",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    result = response.json()

    assert result["record"]["id"] == UUID
    assert isinstance(result["record"]["id"], str)

    assert result["record"]["experiments"][0] == {
        "node_id": "f7bc3db5-4d4c-4c50-9124-0434a66a51a2",
        "submitter_id": "dataset-46-version-2",
    }
    assert isinstance(result["record"]["experiments"][0], dict)

    assert result["record"]["type"] == "case"
    assert isinstance(result["record"]["type"], str)

    assert result["record"]["project_id"] == Gen3Config.GEN3_PUBLIC_ACCESS
    assert isinstance(result["record"]["project_id"], str)

    assert result["record"]["submitter_id"] == "dataset-46-version-2-subjects-sub-11011"
    assert isinstance(result["record"]["submitter_id"], str)

    assert result["record"]["age"] == "12 weeks"
    assert isinstance(result["record"]["age"], str)

    assert result["record"]["pool_id"] == "pool-1"
    assert isinstance(result["record"]["pool_id"], str)

    assert result["record"]["rrid_for_strain"] == "RRID:RGD_737903"
    assert isinstance(result["record"]["rrid_for_strain"], str)

    assert result["record"]["sex"] == "Male"
    assert isinstance(result["record"]["sex"], str)

    assert result["record"]["species"] == "Rattus norvegicus"
    assert isinstance(result["record"]["species"], str)

    assert result["record"]["strain"] == "Sprague-Dawley"
    assert isinstance(result["record"]["strain"], str)

    assert result["record"]["subject_id"] == "sub-11011"
    assert isinstance(result["record"]["subject_id"], str)

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

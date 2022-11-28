from sgqlc.types.relay import Node
from sgqlc.types import String, Int, Type, Field, list_of


class SubDatasetDescriptionNode(Node):
    keywords = list_of(String)
    number_of_samples = String
    number_of_subjects = String
    subtitle = String
    title = String


class ExperimentNode(Node):
    submitter_id = String
    dataset_descriptions = list_of(SubDatasetDescriptionNode)


class DatasetDescriptionNode(Node):
    id = String
    submitter_id = String
    type = String
    project_id = String
    created_datetime = String
    updated_datetime = String
    acknowledgments = String
    contributor_affiliation = list_of(String)
    contributor_name = list_of(String)
    contributor_orcid = list_of(String)
    contributor_role = list_of(String)
    dataset_type = String
    funding = String
    identifier = String
    identifier_description = String
    identifier_type = String
    keywords = list_of(String)
    metadata_version = String
    number_of_samples = Int
    number_of_subjects = Int
    relation_type = String
    state = String
    study_approach = String
    study_collection_title = String
    study_data_collection = String
    study_organ_system = String
    study_primary_conclusion = String
    study_purpose = String
    study_technique = String
    subtitle = String
    title = String


class ManifestNode(Node):
    submitter_id = String
    additional_types = String


class Query(Type):
    experiment = Field(
        ExperimentNode,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
            "submitter_id": list_of(String),
        }
    )
    datasetDescription = Field(
        DatasetDescriptionNode,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
            "submitter_id": String,
            "funding": list_of(String),
        }
    )
    manifest = Field(
        ManifestNode,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
            "submitter_id": list_of(String),
            "additional_types": list_of(String)
        }
    )

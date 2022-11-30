from sgqlc.types.relay import Node
from sgqlc.types import String, Int, Type, Field, list_of


class SubDatasetDescriptionNode(Node):
    title = String
    subtitle = String
    number_of_subjects = Int
    number_of_samples = Int
    keywords = list_of(String)


class ExperimentNode(Node):
    submitter_id = String
    dataset_descriptions = list_of(SubDatasetDescriptionNode)


class DatasetDescriptionNode(Node):
    type = String
    title = String
    subtitle = String
    submitter_id = String
    study_technique = String
    study_purpose = String
    study_primary_conclusion = String
    study_organ_system = String
    study_data_collection = String
    study_approach = String
    relation_type = String
    number_of_subjects = Int
    number_of_samples = Int
    metadata_version = String
    keywords = list_of(String)
    identifier_type = String
    identifier_description = String
    identifier = String
    dataset_type = String
    contributor_role = list_of(String)
    contributor_orcid = list_of(String)
    contributor_name = list_of(String)
    contributor_affiliation = list_of(String)
    acknowledgments = String
    funding = list_of(String)
    study_collection_title = String


class ManifestNode(Node):
    type = String
    timestamp = String
    submitter_id = String
    filename = String
    file_type = String
    description = String
    additional_metadata = list_of(String)
    additional_types = String
    is_derived_from = list_of(String)
    is_described_by = list_of(String)
    is_source_of = list_of(String)
    supplemental_json_metadata = String


class Query(Type):
    experiment = Field(
        ExperimentNode,
        args={
            "first": Int,
            "offset": Int,
            "submitter_id": list_of(String),
        }
    )
    datasetDescription = Field(
        DatasetDescriptionNode,
        args={
            "first": Int,
            "offset": Int,
            "submitter_id": list_of(String),
        }
    )
    manifest = Field(
        ManifestNode,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
            "additional_types": list_of(String)
        }
    )

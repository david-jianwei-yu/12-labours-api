from sgqlc.types.relay import Node
from sgqlc.types import String, Type, Field, list_of


class ExperimentNode(Node):
    submitter_id = String


class DatasetDescriptionNode(Node):
    id = String
    experiments = list_of(ExperimentNode)
    submitter_id = String
    contributor_affiliation = list_of(String)
    contributor_name = list_of(String)
    contributor_orcid = list_of(String)
    contributor_role = list_of(String)
    dataset_type = String
    identifier = String
    identifier_description = String
    identifier_type = String
    keywords = list_of(String)
    metadata_version = String
    number_of_samples = String
    number_of_subjects = String
    relation_type = String
    study_approach = String
    study_data_collection = String
    study_organ_system = String
    study_primary_conclusion = String
    study_purpose = String
    study_technique = String
    subtitle = String
    title = String
    acknowledgments = String
    funding = String


class ManifestNode(Node):
    submitter_id = String
    description = String
    file_type = String
    filename = String
    timestamp = String
    additional_types = String
    is_source_of = String
    is_derived_from = String
    supplemental_json_metadata = String
    id = String


class Query(Type):
    datasetDescription = Field(
        DatasetDescriptionNode,
        args={
            'first': int,
            'study_organ_system': list_of(String),
        }
    )
    manifest = Field(
        ManifestNode,
        args={
            'first': int,
        }
    )

from sgqlc.types.relay import Node
from sgqlc.types import String, Int, Boolean, Type, Field, list_of


class SubExperimentNode(Node):
    id = String
    submitter_id = String


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
    experiments = list_of(SubExperimentNode)


class ManifestNode(Node):
    id = String
    submitter_id = String
    type = String
    project_id = String
    created_datetime = String
    updated_datetime = String
    additional_metadata = String
    additional_types = String
    description = String
    file_type = String
    filename = String
    is_derived_from = list_of(String)
    is_described_by = list_of(String)
    is_source_of = list_of(String)
    state = String
    supplemental_json_metadata = String
    timestamp = String
    experiments = list_of(SubExperimentNode)


class SubManifestNode(Node):
    id = String
    submitter_id = String


class ExperimentNode(Node):
    id = String
    submitter_id = String
    type = String
    project_id = String
    created_datetime = String
    updated_datetime = String
    associated_experiment = String
    copy_numbers_identified = Boolean
    data_description = String
    experimental_description = String
    experimental_intent = String
    indels_identified = Boolean
    marker_panel_description = String
    number_experimental_group = Int
    number_samples_per_experimental_group = Int
    somatic_mutations_identified = Boolean
    state = String
    type_of_data = String
    type_of_sample = String
    type_of_specimen = String
    dataset_descriptions = list_of(DatasetDescriptionNode)
    manifests = list_of(SubManifestNode)


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

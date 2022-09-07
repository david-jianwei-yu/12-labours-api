from sgqlc.types.relay import Node
from sgqlc.types import String, Type, Field, list_of


class DatasetDescriptionNode(Node):
    id = String
    submitter_id = String
    contributor_affiliation = String
    contributor_name = String
    contributor_orcid = String
    contributor_role = String
    dataset_type = String
    identifier = String
    identifier_description = String
    identifier_type = String
    keywords = String
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
    study_collection_title = String


class CaseNode(Node):
    id = String
    submitter_id = String
    age = String
    age_category = String
    rrid_for_strain = String
    sex = String
    species = String
    protocol_title = String
    protocol_url_or_doi = String


class SlideNode(Node):
    id = String
    submitter_id = String
    description = String
    file_type = String
    filename = String
    additional_metadata = String


class Query(Type):
    case = Field(
        CaseNode,
        args={
            'sex': list_of(String),
            'species': list_of(String),
            'quick_search': String,
        }
    )
    datasetDescription = Field(
        DatasetDescriptionNode,
        args={
            'study_organ_system': list_of(String),
            'quick_search': String,
        }
    )
    slide = Field(
        SlideNode,
        args={
            'file_type': list_of(String),
            'quick_search': String,
        }
    )

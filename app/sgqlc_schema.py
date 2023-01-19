from sgqlc.types.relay import Node
from sgqlc.types import String, Int, Type, Field, list_of


# FILTER USE ONLY
# Minimize the query fields
# Increase the generating speed
class DatasetDescriptionFilter(Node):
    submitter_id = String
    keywords = list_of(String)
    study_organ_system = list_of(String)


class ManifestFilter(Node):
    submitter_id = String
    additional_types = list_of(String)


class CaseFilter(Node):
    submitter_id = String
    species = String
    sex = String
    age_category = String


# QUERY USE ONLY
class SubCaseNode(Node):
    species = String


class SubManifestNode(Node):
    filename = String


class SubDatasetDescriptionNode(Node):
    title = String
    subtitle = String
    study_organ_system = list_of(String)
    number_of_subjects = Int
    number_of_samples = Int
    keywords = list_of(String)


class ExperimentNode(Node):
    submitter_id = String
    dataset_descriptions = list_of(SubDatasetDescriptionNode)
    manifests = list_of(SubManifestNode)
    cases = list_of(SubCaseNode)


class DatasetDescriptionNode(Node):
    type = String
    title = String
    subtitle = String
    submitter_id = String
    study_technique = String
    study_purpose = String
    study_primary_conclusion = String
    study_organ_system = list_of(String)
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
    # acknowledgments = String
    # funding = list_of(String)
    # study_collection_title = String


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


class CaseNode(Node):
    type = String
    submitter_id = String
    subject_id = String
    subject_experimental_group = String
    strain = String
    species = String
    sex = String
    rrid_for_strain = String
    pool_id = String
    member_of = String
    also_in_dataset = String
    age_category = String
    age = String
    # age_range_max = String
    # age_range_min = String
    # date_of_birth = String
    # disease_model = String
    # disease_or_disorder = String
    # experiment_date = String
    # experimental_log_file_path = String
    # genotype = String
    # handedness = String
    # intervention = String
    # laboratory_internal_id = String
    # phenotype = String
    # protocol_title = String
    # protocol_url_or_doi = String
    # reference_atlas = String


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
    datasetDescriptionFilter = Field(
        DatasetDescriptionFilter,
        args={
            "first": Int,
            "offset": Int,
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
    manifestFilter = Field(
        ManifestFilter,
        args={
            "first": Int,
            "offset": Int,
            "additional_types": list_of(String)
        }
    )
    case = Field(
        CaseNode,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
        }
    )
    caseFilter = Field(
        CaseFilter,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
            "species": list_of(String),
            "sex": list_of(String),
            "age_category": list_of(String),
        }
    )

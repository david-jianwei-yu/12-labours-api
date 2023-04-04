from sgqlc.types.relay import Node
from sgqlc.types import String, Int, Type, Field, list_of


# FILTER USE ONLY
# Minimize the query fields
# Increase the generating speed
class SubExperiment(Node):
    submitter_id = String


class DatasetDescriptionFilter(Node):
    experiments = list_of(SubExperiment)
    keywords = list_of(String)
    study_organ_system = list_of(String)


class ManifestFilter(Node):
    experiments = list_of(SubExperiment)
    additional_types = list_of(String)


class CaseFilter(Node):
    experiments = list_of(SubExperiment)
    species = String
    sex = String
    age_category = String


# QUERY USE ONLY
class DatasetDescriptionQuery(Node):
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


class ManifestQuery(Node):
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


class CaseQuery(Node):
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


class ExperimentQuery(Node):
    submitter_id = String
    dataset_descriptions = list_of(DatasetDescriptionQuery)
    manifests1 = list_of(ManifestQuery)
    manifests2 = list_of(ManifestQuery)
    manifests3 = list_of(ManifestQuery)
    manifests4 = list_of(ManifestQuery)
    cases = list_of(CaseQuery)


# PAGINATION USE ONLY
class SubDatasetDescription(Node):
    title = String
    study_organ_system = list_of(String)
    number_of_subjects = Int
    number_of_samples = Int
    keywords = list_of(String)
    contributor_name = list_of(String)


class SubManifest(Node):
    filename = String
    file_type = String
    additional_types = String
    is_derived_from = list_of(String)
    is_described_by = list_of(String)
    is_source_of = list_of(String)
    supplemental_json_metadata = String


class SubCase(Node):
    species = String


class ExperimentPagination(Node):
    submitter_id = String
    dataset_descriptions = list_of(SubDatasetDescription)
    manifests1 = list_of(SubManifest)
    manifests2 = list_of(SubManifest)
    manifests3 = list_of(SubManifest)
    manifests4 = list_of(SubManifest)
    cases = list_of(SubCase)


class Query(Type):
    # FILTER
    datasetDescriptionFilter = Field(
        DatasetDescriptionFilter,
        args={
            "first": Int,
            "offset": Int,
            # "study_organ_system": list_of(String),
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
    caseFilter = Field(
        CaseFilter,
        args={
            "first": Int,
            "offset": Int,
            "species": list_of(String),
            "sex": list_of(String),
            "age_category": list_of(String),
        }
    )
    # QUERY
    experimentQuery = Field(
        ExperimentQuery,
        args={
            "first": Int,
            "offset": Int,
            "submitter_id": list_of(String),
        }
    )
    datasetDescriptionQuery = Field(
        DatasetDescriptionQuery,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
        }
    )
    manifestQuery = Field(
        ManifestQuery,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
        }
    )
    caseQuery = Field(
        CaseQuery,
        args={
            "first": Int,
            "offset": Int,
            "quick_search": String,
        }
    )
    # PAGINATION
    experimentPagination = Field(
        ExperimentPagination,
        args={
            "first": Int,
            "offset": Int,
            "submitter_id": list_of(String),
        }
    )

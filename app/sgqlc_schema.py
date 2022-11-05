from sgqlc.types.relay import Node
from sgqlc.types import String, Int, Type, Field, list_of


class SubExperimentNode(Node):
    submitter_id = String


class DatasetDescriptionNode(Node):
    experiments = list_of(SubExperimentNode)


class SubDatasetDescriptionNode(Node):
    submitter_id = String
    keywords = list_of(String)
    subtitle = String
    title = String


class ManifestNode(Node):
    additional_types = String
    submitter_id = String
    experiments = list_of(SubExperimentNode)


# class SubManifestNode(Node):
#     submitter_id = String


class ExperimentNode(Node):
    submitter_id = String
    dataset_descriptions = list_of(SubDatasetDescriptionNode)
    # manifests = list_of(SubManifestNode)


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

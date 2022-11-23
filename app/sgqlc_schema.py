from sgqlc.types.relay import Node
from sgqlc.types import String, Int, Type, Field, list_of


class SubDatasetDescriptionNode(Node):
    submitter_id = String
    keywords = list_of(String)
    subtitle = String
    title = String


class ExperimentNode(Node):
    submitter_id = String
    dataset_descriptions = list_of(SubDatasetDescriptionNode)


class DatasetDescriptionNode(Node):
    submitter_id = String


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

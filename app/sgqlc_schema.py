from sgqlc.types.relay import Node
from sgqlc.types import String, Type, Field, list_of


class SlideNode(Node):
    id = String
    submitter_id = String
    description = String
    file_type = String
    filename = String
    additional_metadata = String


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


class Query(Type):
    slide = Field(
        SlideNode,
        args={
            'file_type': list_of(String),
            'quick_search': String,
        }
    )
    case = Field(
        CaseNode,
        args={
            'sex': list_of(String),
            'species': list_of(String),
            'quick_search': String,
        }
    )

from sgqlc.types.relay import Node
from sgqlc.types import String, Type, Field, list_of


class SlideNode(Node):
    id = String
    submitter_id = String
    description = String
    file_type = String
    filename = String
    additional_metadata = String


class Query(Type):
    slide = Field(
        SlideNode,
        args={
            'additional_metadata': list_of(String),
            'file_type': list_of(String),
            'quick_search': String,
        }
    )

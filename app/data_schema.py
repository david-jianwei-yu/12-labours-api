from typing import Union
from pydantic import BaseModel
from enum import Enum

from app.config import iRODSConfig

BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
INTERNAL_SERVER_ERROR = 500


class ProgramParam(str, Enum):
    demo1 = "demo1"


class Gen3Item(BaseModel):
    program: Union[str, None] = None
    project: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "program": "demo1",
                "project": "12L",
            }
        }


class NodeParam(str, Enum):
    experiment = "experiment"
    dataset_description = "dataset_description"
    manifest = "manifest"
    case = "case"


class GraphQLQueryItem(BaseModel):
    page: Union[int, None] = 1
    limit: Union[int, None] = 0
    node: Union[str, None] = None
    filter: Union[dict, None] = {}
    search: Union[str, None] = ""

    class Config:
        schema_extra = {
            "example": {
                "node": "dataset_description",
                "filter": {
                    "submitter_id": [
                        "dataset-102-version-4-dataset_description"
                    ]
                },
                "search": "",
            }
        }


class GraphQLPaginationItem(BaseModel):
    node: Union[str, None] = "experiment"
    page: Union[int, None] = 1
    limit: Union[int, None] = 50
    filter: Union[dict, None] = {}
    search: Union[dict, None] = {}
    relation: Union[str, None] = "and"

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 50,
                "filter": {},
                "relation": "and"
            }
        }


class ProjectParam(str, Enum):
    project = "12L"


class FormatParam(str, Enum):
    json = "json"
    tsv = "tsv"


class CollectionItem(BaseModel):
    path: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "path": f"{iRODSConfig.IRODS_ENDPOINT_URL}/dataset-102-version-4",
            }
        }


class ActionParam(str, Enum):
    preview = "preview"
    download = "download"

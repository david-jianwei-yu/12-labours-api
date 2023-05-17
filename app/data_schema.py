from typing import Union
from pydantic import BaseModel
from enum import Enum

from app.config import iRODSConfig

BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
INTERNAL_SERVER_ERROR = 500


program_responses = {
    200: {
        "description": "Successfully return a list of Gen3 program name",
        "content": {"application/json": {"example": {"program": []}}}
    }
}


class ProgramParam(str, Enum):
    demo1 = "demo1"


project_responses = {
    200: {
        "description": "Successfully return a list of Gen3 project name",
        "content": {"application/json": {"example": {"project": []}}}
    }
}


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


dictionary_responses = {
    200: {
        "description": "Successfully return a list of Gen3 dictionary name",
        "content": {"application/json": {"example": {"dictionary": []}}}
    }
}


class NodeParam(str, Enum):
    experiment = "experiment"
    dataset_description = "dataset_description"
    manifest = "manifest"
    case = "case"


records_responses = {
    200: {
        "description": "Successfully return a list of json object contains all records metadata within a node",
        "content": {"application/json": {"example": {
            "data": [{"project_id": "", "submitter_id": "", "id": "", "type": "experiment"}]
        }}}
    }
}


record_responses = {
    200: {
        "description": "Successfully return a json object contains gen3 record metadata",
        "content": {"application/json": {"example": [{
            "id": "", "type": "experiment", "project_id": "", "submitter_id": "",
            "associated_experiment": "", "copy_numbers_identified": "", "data_description": "", "experimental_description": "",
            "experimental_intent": "", "indels_identified": "", "marker_panel_description": "", "number_experimental_group": "",
            "number_samples_per_experimental_group": "", "somatic_mutations_identified": "", "type_of_data": "", "type_of_sample": "",
            "type_of_specimen": ""
        }]}}
    },
    404: {"content": {"application/json": {"example": {"detail": "Unable to find xxx and check if the correct project or uuid is used"}}}}
}


class GraphQLQueryItem(BaseModel):
    node: Union[str, None] = None
    filter: Union[dict, None] = {}
    search: Union[str, None] = ""

    class Config:
        schema_extra = {
            "example": {
                "node": "experiment_query",
                "filter": {"submitter_id": ["dataset-102-version-4"]},
                "search": "",
            }
        }


query_responses = {
    200: {
        "description": "Successfully return a list of queried datasets",
        "content": {"application/json": {"example": [{
            "cases": [], "dataset_descriptions": [],  "id": "", "plots": [], "scaffoldViews": [], "scaffolds": [], "submitter_id": "", "thumbnails": []
        }]}}
    }
}


class GraphQLPaginationItem(BaseModel):
    node: Union[str, None] = "experiment_pagination"
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


pagination_responses = {
    200: {
        "description": "Successfully return a list of datasets information",
        "content": {"application/json": {"example": {
            "items": [{"data_url": "", "source_url_prefix": "", "contributors": [], "keywords": [], "numberSamples": 0, "numberSubjects": 0, "name": "", "datasetId": "", "organs": [], "species": [], "plots": [], "scaffoldViews": [], "scaffolds": [], "thumbnails": [], "detailsReady": True}]
        }}}
    }
}


filter_responses = {
    200: {
        "description": "Successfully return filter information",
        "content": {"application/json": {"example": {
            "normal": {"size": 0, "titles": [], "nodes": [], "fields": [], "elements": [], "ids": []},
            "sidebar": [{"key": "", "label": "", "children": [{"facetPropPath": "",  "label": ""}]}]
        }}}
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


root_responses = {
    200: {
        "description": "Successfully return all folders/files name and path under root folder",
        "content": {"application/json": {"example": {
            "folders": [], "files": []
        }}}
    }
}


sub_responses = {
    200: {
        "description": "Successfully return all folders/files name and path under selected folder",
        "content": {"application/json": {"example": {
            "folders": [], "files": []
        }}}
    },
    404: {"content": {"application/json": {"example": {
        "detail": "Data not found in the provided path"
    }}}}
}


class ActionParam(str, Enum):
    preview = "preview"
    download = "download"

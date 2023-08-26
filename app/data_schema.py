from enum import Enum
from typing import Union
from pydantic import BaseModel

from app.config import Gen3Config

title = "12 Labours Portal"

contact = {
    "name": "Auckland Bioengineering Institute",
    "url": "https://www.auckland.ac.nz/en/abi.html",
    # "email": "bioeng-enquiries@auckland.ac.nz",
}

description = """
## Access

You will be able to:

* **Create Gen3 access based on authority**
* **Revoke Gen3 access**

## Gen3

You will be able to:

* **Get Gen3 program/project**
* **Get Gen3 node dictionary**
* **Get Gen3 record(s) metadata**
* **Use GraphQL query Gen3 metadata**
* **Download Gen3 metadata file**

## iRODS

You will be able to:

* **Get iRODS root/sub-folder(s)/sub-file(s)**
* **Download iRODS data file**

## Orthanc

You will be able to:

* **Get Orthanc dicom file instance ids**
* **Download Orthanc dicom file**
"""

tags_metadata = [
    {
        "name": "Gen3",
        "description": "Gen3 is a data platform for building data commons and data ecosystems",
        "externalDocs": {
            "description": "Gen3 official website",
            "url": "https://gen3.org/",
        },
    },
    {
        "name": "iRODS",
        "description": "iRODS is an open source data management software",
        "externalDocs": {
            "description": "iRODS official website",
            "url": "https://irods.org/",
        },
    },
    {
        "name": "Orthanc",
        "description": "Orthanc is a free and open-source, lightweight DICOM server for medical imaging",
        "externalDocs": {
            "description": "Orthanc official website",
            "url": "https://www.orthanc-server.com/",
        },
    },
]


class IdentityItem(BaseModel):
    identity: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "identity": "fakeemail@gmail.com>machine_id",
            }
        }


access_token_responses = {
    200: {
        "description": "Successfully return the gen3 access token",
        "content": {"application/json": {"example": {"identity": "", "access_token": ""}}},
    },
    400: {"content": {"application/json": {"example": {"detail": "Missing field in the request body"}}}}
}


access_revoke_responses = {
    200: {
        "description": "Successfully remove the gen3 access",
        "content": {"application/json": {"example": {"detail": "Revoke access successfully"}}},
    },
    401: {"content": {"application/json": {"example": {"detail": "Unable to remove default access authority"}}}}
}


dictionary_responses = {
    200: {
        "description": "Successfully return a list of Gen3 dictionary name",
        "content": {"application/json": {"example": {"dictionary": []}}}
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


class ModeParam(str, Enum):
    data = "data"
    detail = "detail"
    facet = "facet"
    mri = "mri"


class GraphQLQueryItem(BaseModel):
    node: Union[str, None] = None
    page: Union[int, None] = None
    limit: Union[int, None] = None
    filter: Union[dict, None] = {}
    search: Union[str, None] = ""
    access: Union[list, None] = [Gen3Config.GEN3_PUBLIC_ACCESS]
    asc: Union[str, None] = None
    desc: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "node": "experiment_query",
                "filter": {"submitter_id": ["dataset-102-version-4"]},
                "search": "",
                "access": [Gen3Config.GEN3_PUBLIC_ACCESS]
            }
        }


query_responses = {
    200: {
        "description": "Successfully return a list of queried datasets",
        "content": {"application/json": {"example": [{
            "cases": [], "dataset_descriptions": [],  "id": "", "plots": [],
            "scaffoldViews": [], "scaffolds": [], "submitter_id": "", "thumbnails": []
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
    access: Union[list, None] = [Gen3Config.GEN3_PUBLIC_ACCESS]
    order: Union[str, None] = "published(asc)"
    asc: Union[str, None] = None
    desc: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 50,
                "filter": {},
                "access": [Gen3Config.GEN3_PUBLIC_ACCESS]
            }
        }


pagination_responses = {
    200: {
        "description": "Successfully return a list of datasets information",
        "content": {"application/json": {"example": {
            "items": [{
                "data_url": "", "source_url_prefix": "", "contributors": [], "keywords": [],
                "numberSamples": 0, "numberSubjects": 0, "name": "", "datasetId": "",
                "organs": [], "species": [], "plots": [], "scaffoldViews": [],
                "scaffolds": [], "thumbnails": [], "detailsReady": True
            }]
        }}}
    }
}


filter_responses = {
    200: {
        "description": "Successfully return filter information",
        "content": {"application/json": {"example": {
            "normal": {
                "size": 0, "titles": [], "nodes": [], "fields": [],
                "elements": [], "ids": []
            },
            "sidebar": [{"key": "", "label": "", "children": [{"facetPropPath": "",  "label": ""}]}]
        }}}
    }
}


class FormatParam(str, Enum):
    json = "json"
    tsv = "tsv"


class CollectionItem(BaseModel):
    path: Union[str, None] = "/"

    class Config:
        schema_extra = {
            "example": {
                "path": "/dataset-102-version-4",
            }
        }


collection_responses = {
    200: {
        "description": "Successfully return all folders/files name and path under selected folder",
        "content": {"application/json": {"example": {"folders": [], "files": []}}}
    },
    400: {"content": {"application/json": {"example": {"detail": "Invalid path format is used"}}}},
    404: {"content": {"application/json": {"example": {"detail": "Data not found in the provided path"}}}}
}


class ActionParam(str, Enum):
    preview = "preview"
    download = "download"


class InstanceItem(BaseModel):
    study: Union[str, None] = None
    series: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "study": "",
                "series": "",
            }
        }


instance_responses = {
    200: {
        "description": "Successfully return all folders/files name and path under selected folder",
        "content": {"application/json": {"example": []}}
    },
    400: {"content": {"application/json": {"example": {"detail": "Missing one or more fields in the request body"}}}},
    401: {"content": {"application/json": {"example": {"detail": "Invalid orthanc username or password are used"}}}},
    404: {"content": {"application/json": {"example": {"detail": "Resource is not found in the orthanc server"}}}}
}

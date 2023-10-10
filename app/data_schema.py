"""
Data schema used by APIs/functions
- docs metadata
- api params
- api items
- api responses
"""
from enum import Enum
from typing import Union

from pydantic import BaseModel

#############
### PARAM ###
#############


class ModeParam(str, Enum):
    """
    Provided modes
    """

    data = "data"
    detail = "detail"
    facet = "facet"
    mri = "mri"


class ActionParam(str, Enum):
    """
    Provided actions
    """

    preview = "preview"
    download = "download"


############
### ITEM ###
############


class IdentityItem(BaseModel):
    """
    Access identity item
    """

    email: Union[str, None] = None
    machine: Union[str, None] = None
    expiration: Union[str, None] = None

    class Config:
        """
        Identity example
        """

        schema_extra = {
            "example": {
                "email": "dummy_email@gmail.com",
                "machine": "dummy_machine_id",
                "expiration": "dummy_expiration_time",
            }
        }


class GraphQLQueryItem(BaseModel):
    """
    Gen3 graphql query item
    """

    node: Union[str, None] = None
    page: Union[int, None] = None
    limit: Union[int, None] = None
    filter: Union[dict, None] = {}
    search: Union[str, None] = ""
    access: Union[list, None] = None
    asc: Union[str, None] = None
    desc: Union[str, None] = None

    class Config:
        """
        Query example
        """

        schema_extra = {
            "example": {
                "node": "experiment_query",
                "filter": {"submitter_id": ["dataset-102-version-4"]},
                "search": "",
            }
        }


class GraphQLPaginationItem(BaseModel):
    """
    Gen3 graphql pagination item
    """

    node: Union[str, None] = "experiment_pagination"
    page: Union[int, None] = 1
    limit: Union[int, None] = 50
    filter: Union[dict, None] = {}
    search: Union[dict, None] = {}
    relation: Union[str, None] = "and"
    access: Union[list, None] = None
    order: Union[str, None] = "published(asc)"
    asc: Union[str, None] = None
    desc: Union[str, None] = None

    class Config:
        """
        Pagination example
        """

        schema_extra = {
            "example": {
                "page": 1,
                "limit": 50,
                "filter": {},
            }
        }


class CollectionItem(BaseModel):
    """
    iRODS collection item
    """

    path: Union[str, None] = "/"

    class Config:
        """
        Collection example
        """

        schema_extra = {
            "example": {
                "path": "/dataset-102-version-4",
            }
        }


class InstanceItem(BaseModel):
    """
    Orthanc instance item
    """

    study: Union[str, None] = None
    series: Union[str, None] = None

    class Config:
        """
        Instance example
        """

        schema_extra = {
            "example": {
                "study": "",
                "series": "",
            }
        }


#####################
### DOCS RESPONSE ###
#####################


access_token_responses = {
    200: {
        "description": "Successfully return the access token",
        "content": {
            "application/json": {"example": {"identity": "", "access_token": ""}}
        },
    },
    400: {
        "content": {
            "application/json": {
                "example": {"detail": "Missing one or more fields in the request body"}
            }
        }
    },
}

one_off_access_responses = {
    200: {
        "description": "Successfully return the one off access token",
        "content": {"application/json": {"example": {"one_off_token": ""}}},
    },
}


access_revoke_responses = {
    200: {
        "description": "Successfully remove the access",
        "content": {
            "application/json": {
                "example": {"detail": "Successfully revoke the access"}
            }
        },
    },
    401: {
        "content": {
            "application/json": {
                "example": {"detail": "Unable to remove default access authority"}
            }
        }
    },
}


record_responses = {
    200: {
        "description": "Successfully return a json object contains gen3 record metadata",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": "",
                        "type": "",
                        "submitter_id": "",
                        "associated_experiment": "",
                        "copy_numbers_identified": "",
                        "data_description": "",
                        "experimental_description": "",
                        "experimental_intent": "",
                        "indels_identified": "",
                        "marker_panel_description": "",
                        "number_experimental_group": "",
                        "number_samples_per_experimental_group": "",
                        "somatic_mutations_identified": "",
                        "type_of_data": "",
                        "type_of_sample": "",
                        "type_of_specimen": "",
                    }
                ]
            }
        },
    },
    404: {
        "content": {
            "application/json": {
                "example": {
                    "detail": "Data does not exist or unable to access the data"
                }
            }
        }
    },
}


query_responses = {
    200: {
        "description": "Successfully return a list of queried datasets",
        "content": {
            "application/json": {
                "example": {
                    "data mode": {
                        "data": {
                            "cases": [],
                            "dataset_descriptions": [],
                            "dicomImages": [],
                            "id": "",
                            "mris": [],
                            "plots": [],
                            "scaffoldViews": [],
                            "scaffolds": [],
                            "submitter_id": "",
                            "thumbnails": [],
                        }
                    },
                    "detail mode": {"detail": {}, "facet": {"filter name": []}},
                    "facet mode": {
                        "facet": [{"facet": "", "term": "", "facetPropPath": ""}]
                    },
                    "mri mode": {"mri": {"file name": []}},
                }
            }
        },
    },
    400: {
        "content": {
            "application/json": {
                "example": {
                    "detail": "Mode detail/facet/mri only available when query one dataset in experiment node"
                }
            }
        }
    },
}


pagination_responses = {
    200: {
        "description": "Successfully return a list of datasets information",
        "content": {
            "application/json": {
                "example": {
                    "items": [
                        {
                            "data_url": "",
                            "source_url_prefix": "",
                            "contributors": [],
                            "keywords": [],
                            "numberSamples": 0,
                            "numberSubjects": 0,
                            "name": "",
                            "datasetId": "",
                            "organs": [],
                            "species": [],
                            "plots": [],
                            "scaffoldViews": [],
                            "scaffolds": [],
                            "thumbnails": [],
                            "mris": [],
                            "dicomImages": [],
                            "detailsReady": True,
                        }
                    ],
                    "numberPerPage": "",
                    "total": "",
                }
            }
        },
    }
}


filter_responses = {
    200: {
        "description": "Successfully return filter information",
        "content": {
            "application/json": {
                "example": {
                    "normal": {
                        "size": 0,
                        "titles": [],
                        "nodes": [],
                        "fields": [],
                        "elements": [],
                        "ids": [],
                    },
                    "sidebar": [
                        {
                            "key": "",
                            "label": "",
                            "children": [{"facetPropPath": "", "label": ""}],
                        }
                    ],
                }
            }
        },
    }
}


collection_responses = {
    200: {
        "description": "Successfully return all folders/files name and path under selected folder",
        "content": {"application/json": {"example": {"folders": [], "files": []}}},
    },
    400: {
        "content": {
            "application/json": {"example": {"detail": "Invalid path format is used"}}
        }
    },
    404: {
        "content": {
            "application/json": {
                "example": {"detail": "Data not found in the provided path"}
            }
        }
    },
}


instance_responses = {
    200: {
        "description": "Successfully return all folders/files name and path under selected folder",
        "content": {"application/json": {"example": []}},
    },
    400: {
        "content": {
            "application/json": {
                "example": {"detail": "Missing one or more fields in the request body"}
            }
        }
    },
    404: {
        "content": {
            "application/json": {
                "example": {"detail": "Resource is not found in the orthanc server"}
            }
        }
    },
}

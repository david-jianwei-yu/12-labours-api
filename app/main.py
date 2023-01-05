import re
import mimetypes

from app.config import Config, Gen3Config, iRODSConfig

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse, Response

from typing import Union
from pydantic import BaseModel
from enum import Enum

from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission

from app.sgqlc import SimpleGraphQLClient
from app.filter import Filter, FIELDS

from irods.session import iRODSSession
from app.search import Search

description = """
## Gen3

You will be able to:

* **Get Gen3 program/project**
* **Get Gen3 node dictionary**
* **Get Gen3 record(s) metadata**
* **Use GraphQL query Gen3 metadata**
* **Download Gen3 file**

## iRODS

You will be able to:

* **Get iRODS root/sub-folder(s)/sub-file(s)**
* **Download iRODS file**
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
]

app = FastAPI(
    title="12 Labours Portal",
    description=description,
    # version="0.0.1",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "Auckland Bioengineering Institute",
        "url": "https://www.auckland.ac.nz/en/abi.html",
        "email": "bioeng-enquiries@auckland.ac.nz",
    },
    # license_info={
    #     "name": "Apache 2.0",
    #     "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    # }
    openapi_tags=tags_metadata
)

# Cross orgins, allow any for now
origins = [
    '*',
]

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BAD_REQUEST = 400
UNAUTHORIZED = 401
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
INTERNAL_SERVER_ERROR = 500


SUBMISSION = None
SESSION = None

sgqlc = SimpleGraphQLClient()
f = Filter()
s = Search()


@ app.on_event("startup")
async def start_up():
    try:
        global SUBMISSION
        GEN3_CREDENTIALS = {
            "api_key": Gen3Config.GEN3_API_KEY,
            "key_id": Gen3Config.GEN3_KEY_ID
        }
        AUTH = Gen3Auth(endpoint=Gen3Config.GEN3_ENDPOINT_URL,
                        refresh_token=GEN3_CREDENTIALS)
        SUBMISSION = Gen3Submission(AUTH)
    except Exception:
        print("Encounter an error while creating the GEN3 auth.")

    try:
        # This function is used to connect to the iRODS server, it requires "host", "port", "user", "password" and "zone" environment variables.
        global SESSION
        SESSION = iRODSSession(host=iRODSConfig.IRODS_HOST,
                               port=iRODSConfig.IRODS_PORT,
                               user=iRODSConfig.IRODS_USER,
                               password=iRODSConfig.IRODS_PASSWORD,
                               zone=iRODSConfig.IRODS_ZONE)
        # SESSION.connection_timeout =
    except Exception:
        print("Encounter an error while creating the iRODS session.")


@ app.get("/", tags=["Root"], response_class=PlainTextResponse)
async def root():
    return "This is the fastapi backend."


#
# Gen3 Data Commons
#


@ app.get("/program", tags=["Gen3"])
async def get_gen3_program():
    """
    Return all programs information from the Gen3 Data Commons.
    """
    try:
        program = SUBMISSION.get_programs()
        program_dict = {"program": []}
        for ele in program["links"]:
            program_dict["program"].append(ele.replace("/v0/submission/", ""))
        return program_dict
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


class Program(str, Enum):
    program = "demo1"


@ app.get("/project/{program}", tags=["Gen3"])
async def get_gen3_project(program: Program):
    """
    Return all projects information from a program.

    :param program: Gen3 program name.
    """
    try:
        project = SUBMISSION.get_projects(program)
        project_dict = {"project": []}
        for ele in project["links"]:
            project_dict["project"].append(
                ele.replace(f"/v0/submission/{program}/", ""))
        return project_dict
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


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


@ app.post("/dictionary", tags=["Gen3"])
async def get_gen3_dictionary(item: Gen3Item):
    """
    Return all dictionary nodes from the Gen3 Data Commons
    """
    if item.program == None or item.project == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one or more fields in the request body")

    try:
        dictionary = SUBMISSION.get_project_dictionary(
            item.program, item.project)
        dictionary_dict = {"dictionary": []}
        for ele in dictionary["links"]:
            dictionary_dict["dictionary"].append(ele.replace(
                f"/v0/submission/{item.program}/{item.project}/_dictionary/", ""))
        return dictionary_dict
    except Exception:
        raise HTTPException(
            status_code=NOT_FOUND, detail=f"Program {item.program} or project {item.project} not found")


class Node(str, Enum):
    experiment = "experiment"
    dataset_description = "dataset_description"
    manifest = "manifest"


@ app.post("/records/{node}", tags=["Gen3"])
async def get_gen3_node_records(node: Node, item: Gen3Item):
    """
    Return all records information in a dictionary node.

    :param node: The dictionary node to export.
    :return: A list of json object containing all records in the dictionary node.
    """
    if item.program == None or item.project == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one or more fields in the request body")

    node_record = SUBMISSION.export_node(
        item.program, item.project, node, "json")
    if "message" in node_record:
        if "unauthorized" in node_record["message"]:
            raise HTTPException(status_code=UNAUTHORIZED,
                                detail=node_record["message"])
        raise HTTPException(status_code=NOT_FOUND,
                            detail=node_record["message"])
    elif node_record["data"] == []:
        raise HTTPException(status_code=NOT_FOUND,
                            detail=f"No data found with node type {node} and check if the correct project or node type is used")
    else:
        return node_record


@ app.post("/record/{uuid}", tags=["Gen3"])
async def get_gen3_record(uuid: str, item: Gen3Item):
    """
    Return record information in the Gen3 Data Commons.

    :param uuid: uuid of the record.
    :return: A list of json object.
    """
    if item.program == None or item.project == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one or more fields in the request body")

    record = SUBMISSION.export_record(
        item.program, item.project, uuid, "json")
    if "message" in record:
        if "unauthorized" in record["message"]:
            raise HTTPException(status_code=UNAUTHORIZED,
                                detail=record["message"])
        raise HTTPException(
            status_code=NOT_FOUND, detail=record["message"]+" and check if the correct project or uuid is used")
    else:
        return record


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
                        "dataset-<dataset_id>-version-<version_id>-dataset_description"
                    ]
                },
                "search": "",
            }
        }


@ app.post("/graphql/query", tags=["Gen3"])
async def graphql_query(item: GraphQLQueryItem):
    """
    Return queries metadata records. The API uses GraphQL query language.

    filter post format should looks like: 
    {
        "<filed_name>": [
            "<attribute_name>", 
            ...
        ], 
        ...
    }

    search post format should be <string_content>,
    and search only available in manifest/case nodes
    """
    query_result = sgqlc.get_queried_result(item, SUBMISSION)
    return query_result[item.node]


def update_pagination_item(item, input):
    if item.filter != {}:
        query_item = GraphQLQueryItem()
        filter_dict = {"submitter_id": []}
        temp_node_dict = {}
        for element in item.filter.values():
            query_item.node, query_item.filter = element["node"], element["filter"]
            filter_node = re.sub('_filter', '', query_item.node)
            filter_field = list(query_item.filter.keys())[0]
            # Only do fetch when there is no related temp data stored in temp_node_dict
            # or the node field type is "String"
            if filter_node not in temp_node_dict.keys() or filter_field not in FIELDS:
                query_result = sgqlc.get_queried_result(query_item, SUBMISSION)
                # The data will be stored when the field type is an "Array"
                # The default filter relation of the Gen3 "Array" type field is "AND"
                # We need "OR", therefore entire node data will go through a self-written filter function
                if filter_field in FIELDS:
                    temp_node_dict[filter_node] = query_result[filter_node]
            elif filter_node in temp_node_dict.keys() and filter_field in FIELDS:
                query_result = temp_node_dict
            filter_dict["submitter_id"].append(f.get_filtered_datasets(
                query_item.filter, query_result[filter_node]))
        item.filter = filter_dict
        f.filter_relation(item)

    if input != "":
        # If input does not match any content in the database, item.search will be empty dictionary
        item.search["submitter_id"] = s.get_searched_datasets(input, SESSION)
        if item.search != {} and ("submitter_id" not in item.filter or item.filter["submitter_id"] != []):
            s.search_filter_relation(item)


class GraphQLPaginationItem(BaseModel):
    page: Union[int, None] = 1
    limit: Union[int, None] = 50
    node: Union[str, None] = None
    filter: Union[dict, None] = {}
    search: Union[dict, None] = {}
    relation: Union[str, None] = "and"

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 50,
                "node": "experiment",
                "filter": {},
                "relation": "and"
            }
        }


@ app.post("/graphql/pagination/", tags=["Gen3"])
async def graphql_pagination(item: GraphQLPaginationItem, search: str = ""):
    """
    /graphql/pagination/?search=<string>

    Return filtered/searched metadata records. The API uses GraphQL query language.

    Default page = 1
    Default limit = 50
    Default search = ""
    Default relation = "and"

    filter post format should looks like: 
    {
        "id": {
            "node": "<gen3_node>", 
            "filter": {
                "<gen3_field>": [
                    <filed_content>,
                    ...
                ]
            }
        }, 
        ...
    }

    :param search: string content.
    """
    update_pagination_item(item, search)
    query_result = sgqlc.get_queried_result(item, SUBMISSION)
    if item.search != {}:
        # Sort only if search is not empty, since search results are sorted by word relevance
        query_result[item.node] = sorted(
            query_result[item.node], key=lambda dict: item.filter["submitter_id"].index(dict["submitter_id"]))
    return {
        "data": query_result[item.node],
        # Maximum number of records display in one page
        "limit": item.limit,
        "page": item.page,
        "total": query_result["total"]
    }


@ app.get("/filter", tags=["Gen3"])
async def generate_filter():
    """
    Return the support data for frontend filters component.
    """
    return f.generate_filter_information()


class Project(str, Enum):
    project = "12L"


class Format(str, Enum):
    json = "json"
    tsv = "tsv"


@ app.get("/metadata/download/{program}/{project}/{uuid}/{format}", tags=["Gen3"])
async def download_gen3_metadata_file(program: Program, project: Project, uuid: str, format: Format):
    """
    Return a single file for a given uuid.

    :param program: program name.
    :param project: project name.
    :param uuid: uuid of the file.
    :param format: file format (must be one of the following: json, tsv).
    :return: A JSON or CSV file contains the metadata.
    """
    try:
        metadata = SUBMISSION.export_record(program, project, uuid, format)
    except Exception as e:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(e))

    if "message" in metadata:
        if "unauthorized" in metadata["message"]:
            raise HTTPException(status_code=UNAUTHORIZED,
                                detail=metadata["message"])
        raise HTTPException(
            status_code=NOT_FOUND, detail=metadata["message"]+" and check if the correct project or uuid is used")
    else:
        if format == "json":
            return JSONResponse(content=metadata[0],
                                media_type="application/json",
                                headers={"Content-Disposition":
                                         f"attachment;filename={uuid}.json"})
        elif format == "tsv":
            return Response(content=metadata,
                            media_type="text/csv",
                            headers={"Content-Disposition":
                                     f"attachment;filename={uuid}.csv"})


#
# iRODS
#


def get_collection_list(data):
    collect_list = []
    for ele in data:
        collect_list.append({
            "name": ele.name,
            "path": ele.path
        })
    return collect_list


@ app.get("/collection/root", tags=["iRODS"])
async def get_irods_root_collections():
    """
    Return all collections from the root folder.
    """
    try:
        collect = SESSION.collections.get(
            f"{iRODSConfig.IRODS_ENDPOINT_URL}")
        folders = get_collection_list(collect.subcollections)
        files = get_collection_list(collect.data_objects)
    except Exception as e:
        raise HTTPException(status_code=INTERNAL_SERVER_ERROR, detail=str(e))
    return {"folders": folders, "files": files}


class CollectionItem(BaseModel):
    path: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "path": "/tempZone/home/rods/datasets",
            }
        }


@ app.post("/collection", tags=["iRODS"])
async def get_irods_collections(item: CollectionItem):
    """
    Return all collections from the required folder.
    """
    if item.path == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing field in the request body")

    try:
        collect = SESSION.collections.get(item.path)
        folders = get_collection_list(collect.subcollections)
        files = get_collection_list(collect.data_objects)
        return {"folders": folders, "files": files}
    except Exception:
        raise HTTPException(status_code=NOT_FOUND,
                            detail="Data not found in the provided path")


class Action(str, Enum):
    preview = "preview"
    download = "download"


@ app.get("/data/{action}/{filepath:path}", tags=["iRODS"])
async def get_irods_data_file(action: Action, filepath: str):
    """
    Used to preview most types of data files in iRODS (.xlsx and .csv not supported yet).
    OR
    Return a specific download file from iRODS or a preview of most types data.

    :param action: Action should be either preview or download.
    :param filepath: Required iRODS file path.
    :return: A file with data.
    """
    chunk_size = 1024*1024
    try:
        file = SESSION.data_objects.get(
            f"{iRODSConfig.IRODS_ENDPOINT_URL}/{filepath}")
    except Exception:
        raise HTTPException(status_code=NOT_FOUND,
                            detail="Data not found in the provided path")

    def iterate_file():
        with file.open("r") as file_like:
            chunk = file_like.read(chunk_size)
            while chunk:
                yield chunk
                chunk = file_like.read(chunk_size)
    if action == "preview":
        return StreamingResponse(iterate_file(),
                                 media_type=mimetypes.guess_type(file.name)[0])
    elif action == "download":
        return StreamingResponse(iterate_file(),
                                 media_type=mimetypes.guess_type(file.name)[
            0],
            headers={"Content-Disposition": f"attachment;filename={file.name}"})
    else:
        raise HTTPException(status_code=METHOD_NOT_ALLOWED,
                            detail="The action is not provided in this API")

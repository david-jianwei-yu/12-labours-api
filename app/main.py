import json
import mimetypes

from app.config import Config, Gen3Config, iRODSConfig
from app.dbtable import StateTable

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse, Response

from typing import Union
from pydantic import BaseModel
from enum import Enum

from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission
from gen3.query import Gen3Query

from app.sgqlc import SimpleGraphQLClient
from app.filter import Filter

from irods.session import iRODSSession

app = FastAPI(
    title="12 Labours Portal APIs"
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

GEN3_CREDENTIALS = {
    "api_key": Gen3Config.GEN3_API_KEY,
    "key_id": Gen3Config.GEN3_KEY_ID
}

statetable = None
SUBMISSION = None
QUERY = None
SESSION = None


@ app.on_event("startup")
async def start_up():
    try:
        global statetable
        statetable = StateTable(Config.DATABASE_URL)
    except AttributeError:
        print("Encounter an error setting up the database")
        statetable = None

    try:
        global SUBMISSION
        global QUERY
        AUTH = Gen3Auth(refresh_token=GEN3_CREDENTIALS)
        SUBMISSION = Gen3Submission(AUTH)
        QUERY = Gen3Query(AUTH)
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


@ app.get("/", response_class=PlainTextResponse)
async def root():
    return "This is the fastapi backend."


@ app.get("/health", response_class=PlainTextResponse)
async def health():
    return json.dumps({"status": "healthy"})


def get_share_link(table):
    # Do not commit to database when testing
    commit = True
    if app.config["TESTING"]:
        commit = False
    if table:
        json_data = request.get_json()
        if json_data and "state" in json_data:
            state = json_data["state"]
            uuid = table.pushState(state, commit)
            return {"uuid": uuid}
        abort(400, description="State not specified")
    else:
        abort(404, description="Database not available")


def get_saved_state(table):
    if table:
        json_data = request.get_json()
        if json_data and "uuid" in json_data:
            uuid = json_data["uuid"]
            state = table.pullState(uuid)
            if state:
                return {"state": table.pullState(uuid)}
        abort(400, description="Key missing or did not find a match")
    else:
        abort(404, description="Database not available")


# An example
@ app.put("/state/getshareid")
async def get_share_link():
    return get_share_link(statetable)


# Get the map state using the share link id.
@ app.get("/state/getstate")
async def get_state():
    return get_saved_state(statetable)


#
# Gen3 Data Commons
#
class program(str, Enum):
    program = "demo1"


class project(str, Enum):
    project = "12L"


class node(str, Enum):
    experiment = "experiment"
    dataset_description = "dataset_description"
    manifest = "manifest"


class format(str, Enum):
    json = "json"
    tsv = "tsv"


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


class GraphQLItem(BaseModel):
    limit: Union[int, None] = 50
    page: Union[int, None] = 1
    node: Union[str, None] = None
    filter: Union[dict, None] = None
    search: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "limit": 50,
                "page": 1,
                "node": "experiment",
                "filter": {},
                "search": ""
            }
        }


@ app.get("/program")
async def get_gen3_program():
    """
    Return all programs' information from the Gen3 Data Commons.
    """
    try:
        program = SUBMISSION.get_programs()
        program_dict = {"program": []}
        for ele in program["links"]:
            program_dict["program"].append(ele.replace("/v0/submission/", ""))
        return program_dict
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


@ app.get("/project/{program}")
async def get_gen3_project(program: program):
    """
    Return all projects' information from a program.

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


@ app.post("/dictionary")
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


@ app.post("/records/{node}")
async def get_gen3_node_records(node: node, item: Gen3Item):
    """
    Return all records' information in a dictionary node.

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


@ app.post("/record/{uuid}")
async def get_gen3_record(uuid: str, item: Gen3Item):
    """
    Return record's information in the Gen3 Data Commons.

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
            status_code=NOT_FOUND, detail=record["message"]+" and check if uses the correct project or uuid is used")
    else:
        return record


def merge_item_filter(item):
    # AND relationship
    count_filter = 0
    id_dict = {}
    filter_dict = {"submitter_id": []}
    if item.filter != {}:
        # Create a id dict to count the frequency of occurrence
        for key in item.filter.keys():
            count_filter += 1
            for ele in item.filter[key]:
                if ele not in id_dict.keys():
                    id_dict[ele] = 1
                else:
                    id_dict[ele] += 1
        # Find the matched id and add them into the dict with key submitter_id
        for id in id_dict.keys():
            if id_dict[id] == max(id_dict.values()):
                filter_dict["submitter_id"].append(id)
        # Replace the filter with created dict
        item.filter = filter_dict


@ app.post("/graphql")
async def graphql_query(item: GraphQLItem):
    """
    Return filtered/searched metadata records. The API uses GraphQL query language.

    Default limit = 50
    Default page = 1

    filter post format should looks like: {"<filed_name>": ["<attribute_name>", ...], ...}

    search post format should looks like: "\<string\>"
    """
    if item.node == None or item.filter == None or item.search == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one ore more fields in request body.")

    if item.node == "experiment":
        merge_item_filter(item)
    sgqlc = SimpleGraphQLClient()
    query = sgqlc.generate_query(item)
    # query_result = QUERY.graphql_query(query)
    query_result = SUBMISSION.query(query)["data"]
    if query_result is not None and query_result[item.node] != []:
        pagination_result = {
            "data": query_result[item.node],
            # Maximum number of records display in one page
            "limit": item.limit,
            # The number of records display in current page
            "size": len(query_result[item.node]),
            "page": item.page,
            "total": query_result["total"]
        }
        return pagination_result
    else:
        raise HTTPException(status_code=NOT_FOUND,
                            detail="Data cannot be found in the node.")

#
# Gen3 Filter
#
filter_list = {
    "manifest": ["DATA TYPES"],
    "dataset_description": ["ANATOMICAL STRUCTURE", "SPECIES"],
}


@ app.post("/filters")
async def generate_filters(item: Gen3Item):
    """
    Return the support data for frontend filters.
    """
    if item.program == None or item.project == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one ore more fields in request body.")

    filters_result = {}
    for node in filter_list:
        for filter in filter_list[node]:
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
                f = Filter()
                filters_result[filter] = f.get_filter_data(
                    filter, node_record)
    return filters_result


@ app.get("/metadata/download/{program}/{project}/{uuid}/{format}")
async def download_gen3_metadata_file(program: str, project: str, uuid: str, format: str):
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
            status_code=NOT_FOUND, detail=metadata["message"]+" and check if uses the correct project or uuid is used")
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


class action(str, Enum):
    preview = "preview"
    download = "download"


class CollectionItem(BaseModel):
    path: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "path": "/tempZone/home/rods/datasets",
            }
        }


def get_collection_list(data):
    collect_list = []
    for ele in data:
        collect_list.append({
            "id": ele.id,
            "name": ele.name,
            "path": ele.path
        })
    return collect_list


@ app.get("/collection")
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
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))
    return {"folders": folders, "files": files}


@ app.post("/collection")
async def get_irods_collections(item: CollectionItem):
    """
    Return all collections from the required folder.
    """
    if item.path == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing field in request body.")

    try:
        collect = SESSION.collections.get(item.path)
        folders = get_collection_list(collect.subcollections)
        files = get_collection_list(collect.data_objects)
        return {"folders": folders, "files": files}
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


@ app.get("/data/{action}/{filepath:path}")
async def get_irods_data_file(action: action, filepath: str):
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
            raise HTTPException(status_code=NOT_FOUND,
                                detail="The action is not provided in this API.")
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))

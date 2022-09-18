import json
import requests
import mimetypes

from app.config import Config, Gen3Config, iRODSConfig
from app.dbtable import StateTable

from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from typing import Union
from pydantic import BaseModel

from irods.session import iRODSSession

from sgqlc.endpoint.http import HTTPEndpoint
from app.sgqlc import SimpleGraphQLClient

from app.filter import Filter

app = FastAPI()

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

statetable = None

# CORS(app)

BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404

GEN3_CREDENTIALS = {
    "api_key": Gen3Config.GEN3_API_KEY,
    "key_id": Gen3Config.GEN3_KEY_ID
}

HEADER = None
SESSION = None


class RecordItem(BaseModel):
    program: Union[str, None] = None
    project: Union[str, None] = None


class GraphQLItem(BaseModel):
    limit: Union[int, None] = None
    page: Union[int, None] = None
    node: Union[str, None] = None
    filter: Union[dict, None] = None
    search: Union[str, None] = None


class GraphQLData(BaseModel):
    data: Union[dict, None] = None


class CollectionItem(BaseModel):
    path: Union[str, None] = None


@ app.on_event("startup")
async def start_up():
    try:
        global statetable
        statetable = StateTable(Config.DATABASE_URL)
    except AttributeError:
        print("Encounter an error setting up the database")
        statetable = None

    try:
        global HEADER
        TOKEN = requests.post(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/user/credentials/cdis/access_token", json=GEN3_CREDENTIALS).json()
        HEADER = {"Authorization": "bearer " + TOKEN["access_token"]}
    except Exception:
        print("Encounter an error while generating a token from GEN3.")

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


@ app.get("/program")
# Get the program information from Gen3 Data Commons
async def get_gen3_program():
    """
    Return the program information from Gen3 Data Commons
    """
    try:
        res = requests.get(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/", headers=HEADER)
        json_data = json.loads(res.content)
        program_list = []
        for ele in json_data["links"]:
            program_list.append(ele.replace(
                "/v0/submission/", ""))
        new_json_data = {"program": program_list}
        return new_json_data
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


@ app.get("/project/{program}")
# Get all projects information from Gen3 Data Commons
async def get_gen3_project(program: str):
    """
    Return project information.

    :param program: Gen3 program name
    """
    try:
        res = requests.get(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{program}", headers=HEADER)
        json_data = json.loads(res.content)
        project_list = []
        for ele in json_data["links"]:
            project_list.append(ele.replace(
                f"/v0/submission/{program}/", ""))
        new_json_data = {"project": project_list}
        return new_json_data
    except Exception as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))


@ app.get("/dictionary")
# Get all dictionary node from Gen3 Data Commons
async def get_gen3_dictionary():
    """
    Return all dictionary node from Gen3 Data Commons
    """
    try:
        res = requests.get(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/_dictionary", headers=HEADER)
        json_data = json.loads(res.content)
        dictionary_list = []
        for ele in json_data["links"]:
            dictionary_list.append(ele.replace(
                "/v0/submission/_dictionary/", ""))
        new_json_data = {"dictionary": dictionary_list}
        return new_json_data
    except Exception as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))


@ app.post("/records/{node}")
# Exports all records in a dictionary node
async def get_gen3_node_records(node: str, item: RecordItem):
    """
    Return all records in a dictionary node.

    :param node: The dictionary node to export.
    :return: A list of json object containing all records in the dictionary node.
    """
    if item.program == None or item.project == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one ore more fields in request body.")

    try:
        res = requests.get(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{item.program}/{item.project}/export/?node_label={node}&format=json", headers=HEADER)
        json_data = json.loads(res.content)
        if b"data" in res.content and json_data["data"] != []:
            return json_data
        else:
            raise HTTPException(status_code=NOT_FOUND,
                                detail="Node records cannot be found.")
    except Exception:
        raise HTTPException(status_code=FORBIDDEN,
                            detail="Invalid program or project name.")


@ app.post("/record/{uuids}")
# Exports one or more records(records must in one node), use comma to separate the uuids
# e.g. uuid1,uuid2,uuid3
async def get_gen3_record(uuids: str, item: RecordItem):
    """
    Return the fields of one or more records in a dictionary node.

    :param uuids: uuids of the records (use comma to separate the uuids e.g. uuid1,uuid2,uuid3).
    :return: A list of json object
    """
    if item.program == None or item.project == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one ore more fields in request body.")

    try:
        res = requests.get(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{item.program}/{item.project}/export/?ids={uuids}&format=json", headers=HEADER)
        json_data = json.loads(res.content)
        if b"id" in res.content:
            return json_data
        else:
            raise HTTPException(status_code=NOT_FOUND,
                                detail="Record can not be found, please check the uuid of the record.")
    except Exception:
        raise HTTPException(status_code=FORBIDDEN,
                            detail="Invalid program or project name.")


# def search_keyword(keyword, data):
#     search_result = []
#     keyword_list = re.findall('([-0-9a-zA-Z]+)', keyword)
#     for ele in data:
#         for word in keyword_list:
#             if word.lower() in json.dumps(ele).lower():
#                 search_result.append(ele)
#     sorted_result = sorted(
#         search_result, key=search_result.count, reverse=True)
#     output_result = []
#     [output_result.append(x) for x in sorted_result if x not in output_result]
#     return output_result


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
    return item


@ app.post("/graphql")
# Only used for filtering and searching the files in a specific node
async def graphql_query(item: GraphQLItem):
    """
    Return filtered metadata records. The query uses GraphQL query.

    Default limit = 50
    Default page = 1

    filter post format should looks like:
    {"<filed_name>": ["<attribute_name>"], ...}

    search post format should looks like:
    "<keyword>"
    """
    if item.limit == None or item.page == None or item.node == None or item.filter == None or item.search == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one ore more fields in request body.")

    # Set default records display number
    if item.limit == None:
        item.limit = 50
    # Set default display page
    if item.page == None:
        item.page = 1
    if item.node == "experiment":
        item = merge_item_filter(item)
    sgqlc = SimpleGraphQLClient()
    query = sgqlc.generate_query(item)
    endpoint = HTTPEndpoint(
        url=f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/graphql/", base_headers=HEADER)
    result = endpoint(query=query)["data"]
    if result is not None and result[item.node] != []:
        # if item.search != "":
        #     result = search_keyword(item.search, result)
        pagination_result = {
            "data": result[item.node],
            # Maximum number of records display in one page
            "limit": item.limit,
            # The number of records display in current page
            "size": len(result[item.node]),
            "page": item.page,
            "total": result["total"]
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


@app.post("/filters")
async def generate_filters(item: RecordItem):
    """
    Return the support data for frontend filters.
    """
    if item.program == None or item.project == None:
        raise HTTPException(status_code=BAD_REQUEST,
                            detail="Missing one ore more fields in request body.")

    try:
        filters_result = {}
        for node in filter_list:
            for filter in filter_list[node]:
                res = requests.get(
                    f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{item.program}/{item.project}/export/?node_label={node}&format=json", headers=HEADER)
                json_data = json.loads(res.content)
                if b"data" in res.content and json_data["data"] != []:
                    f = Filter()
                    filters_result[filter] = f.get_filter_data(
                        filter, json_data)
                else:
                    raise HTTPException(status_code=NOT_FOUND,
                                        detail="Mimetypes filter data cannot be generated.")
        return filters_result
    except Exception:
        raise HTTPException(status_code=FORBIDDEN,
                            detail="Invalid program or project name.")


@ app.get("/download/metadata/{program}/{project}/{uuid}/{format}")
async def download_gen3_metadata_file(program: str, project: str, uuid: str, format: str):
    """
    Return a single file for a given uuid.

    :param program: program name.
    :param project: project name.
    :param uuid: uuid of the file.
    :param format: format of the file (must be one of the following: json, tsv).
    :return: A JSON or CSV file containing the metadata.
    """
    try:
        res = requests.get(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{program}/{project}/export/?ids={uuid}&format={format}", headers=HEADER)
        if format == "json":
            return Response(content=res.content,
                            media_type="application/json",
                            headers={"Content-Disposition":
                                     f"attachment;filename={uuid}.json"})
        else:
            return Response(content=res.content,
                            media_type="text/csv",
                            headers={"Content-Disposition":
                                     f"attachment;filename={uuid}.csv"})
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


#
# iRODS
#


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
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))
    folders = get_collection_list(collect.subcollections)
    files = get_collection_list(collect.data_objects)
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


@ app.get("/preview/data/{filepath:path}")
async def preview_irods_data_file(filepath: str):
    """
    Used to preview most types of data files in iRODS (.xlsx and .csv not supported yet).

    :param filepath: Required iRODS file path.
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
        return StreamingResponse(iterate_file(),
                                 media_type=mimetypes.guess_type(file.name)[0])
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


@ app.get("/download/data/{filepath:path}")
async def download_irods_data_file(filepath: str):
    """
    Return a specific download file from iRODS or a preview of most types data.

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
        return StreamingResponse(iterate_file(),
                                 media_type=mimetypes.guess_type(file.name)[0],
                                 headers={"Content-Disposition": f"attachment;filename={file.name}"})
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))

import re
import time
import mimetypes


from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse, Response
from fastapi_utils.tasks import repeat_every
from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission
from irods.session import iRODSSession

from app.config import *
from app.data_schema import *
from app.filter_dictionary import FilterGenerator
from app.filter import Filter
from app.pagination import Pagination
from app.search import Search
from app.sgqlc import SimpleGraphQLClient
from middleware.auth import Authenticator

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
    # version="",
    # terms_of_service="",
    contact={
        "name": "Auckland Bioengineering Institute",
        "url": "https://www.auckland.ac.nz/en/abi.html",
        # "email": "bioeng-enquiries@auckland.ac.nz",
    },
    # license_info={
    #     "name": "",
    #     "url": "",
    # }
    openapi_tags=tags_metadata,
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

SUBMISSION = None
SESSION = None
SESSION_CONNECTED = False
FILTER_GENERATED = False
fg = None
f = Filter()
p = None
s = None
sgqlc = None
a = Authenticator()


def check_irods_session():
    try:
        global SESSION_CONNECTED
        SESSION.collections.get(iRODSConfig.IRODS_ENDPOINT_URL)
        print("Successfully connected to the iRODS session.")
        SESSION_CONNECTED = True
    except Exception:
        print("Encounter an error while connecting to the iRODS session.")
        SESSION_CONNECTED = False


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
        check_irods_session()
    except Exception:
        print("Encounter an error while creating the iRODS session.")

    global s, sgqlc, fg, p
    s = Search(SESSION)
    sgqlc = SimpleGraphQLClient(SUBMISSION)
    fg = FilterGenerator(sgqlc)
    p = Pagination(fg, f, s, sgqlc)


@ app.on_event("startup")
@repeat_every(seconds=60*60*24)
def periodic_execution():
    global FILTER_GENERATED
    FILTER_GENERATED = False
    while not FILTER_GENERATED:
        FILTER_GENERATED = fg.generate_filter_dictionary()
    if FILTER_GENERATED:
        print("Default filter dictionary has been updated.")


@ app.get("/", tags=["Root"], response_class=PlainTextResponse)
async def root():
    return "This is the fastapi backend."


#########################
### Gen3              ###
### Gen3 Data Commons ###
#########################


def split_access(access):
    access_list = access[0].split("-")
    return access_list[0], access_list[1]


def update_name_list(data, name, path):
    name_dict = {name: []}
    for ele in data["links"]:
        ele = ele.replace(path, "")
        if name == "access":
            ele = re.sub('/', '-', ele)
        name_dict[name].append(ele)
    return name_dict


@ app.post("/access/token", tags=["Access"], summary="Create gen3 access token for authorized user", responses=access_token_responses)
async def create_gen3_access(item: EmailItem):
    if item.email == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing field in the request body")

    result = {
        "email": item.email,
        "access_token": a.generate_access_token(item.email, SESSION)
    }
    return result


@ app.delete("/access/revoke", tags=["Access"], summary="Revoke gen3 access for authorized user", responses=access_revoke_responses)
async def revoke_gen3_access(revoked: bool = Depends(a.revoke_user_authority)):
    if revoked:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail="Revoke successfully")


@ app.get("/access/authorize", tags=["Access"], summary="Get gen3 access authorize", responses=access_authorize_responses)
async def get_gen3_access(access: dict = Depends(a.get_user_access_scope)):
    """
    Return all programs/projects information from the Gen3 Data Commons.

    Use {"Authorization": "Bearer publicaccesstoken"} for accessing public program/project
    """
    try:
        program = SUBMISSION.get_programs()
        program_dict = update_name_list(program, "program", "/v0/submission/")
        restrict_program = list(
            set(access["policies"]).intersection(program_dict["program"]))
        project = {"links": []}
        for prog in restrict_program:
            project["links"] += SUBMISSION.get_projects(prog)["links"]
        return update_name_list(project, "access", "/v0/submission/")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@ app.post("/dictionary", tags=["Gen3"], summary="Get gen3 dictionary information", responses=dictionary_responses)
async def get_gen3_dictionary(item: AccessItem):
    """
    Return all dictionary nodes from the Gen3 Data Commons
    """
    try:
        program, project = split_access(item.access)
        dictionary = SUBMISSION.get_project_dictionary(program, project)
        return update_name_list(dictionary, "dictionary", f"/v0/submission/{program}/{project}/_dictionary/")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Program {program} or project {project} not found")


@ app.post("/records/{node}", tags=["Gen3"], summary="Get gen3 node records information", responses=records_responses)
async def get_gen3_node_records(node: NodeParam, item: AccessItem):
    """
    Return all records information in a dictionary node.

    - **node**: The dictionary node to export.
    """
    program, project = split_access(item.access)
    node_record = SUBMISSION.export_node(program, project, node, "json")
    if "message" in node_record:
        if "unauthorized" in node_record["message"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=node_record["message"])
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=node_record["message"])
    elif node_record["data"] == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No data found with node type {node} and check if the correct project or node type is used")
    else:
        return node_record


@ app.post("/record/{uuid}", tags=["Gen3"], summary="Get gen3 record information", responses=record_responses)
async def get_gen3_record(uuid: str, item: AccessItem):
    """
    Return record information in the Gen3 Data Commons.

    - **uuid**: uuid of the record.
    """
    program, project = split_access(item.access)
    record = SUBMISSION.export_record(program, project, uuid, "json")
    if "message" in record:
        if "unauthorized" in record["message"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=record["message"])
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=record["message"]+" and check if the correct project or uuid is used")
    else:
        return record


@ app.post("/graphql/query", tags=["Gen3"], summary="GraphQL query gen3 information", responses=query_responses)
async def graphql_query(item: GraphQLQueryItem):
    """
    Return queries metadata records. The API uses GraphQL query language.

    **node**
    - experiment_query
    - dataset_description_query
    - manifest_query
    - case_query

    **filter**
    - {"field_name": ["<field_value>", ...], ...}

    **search**
    - string content,
    - only available in dataset_description/manifest/case nodes
    """
    query_result = sgqlc.get_queried_result(item)
    return query_result[item.node]


@ app.post("/graphql/pagination/", tags=["Gen3"], summary="Display datasets", responses=pagination_responses)
async def graphql_pagination(item: GraphQLPaginationItem, search: str = ""):
    """
    /graphql/pagination/?search=<string>

    Return filtered/searched metadata records. The API uses GraphQL query language.

    - Default page = 1
    - Default limit = 50
    - Default filter = {}
    - Default search = ""
    - Default relation = "and"

    **node**
    - experiment_pagination

    **filter(zero or more)** 
    - {"\\<id\\>": {"node": "<gen3_node>", "filter": {"<gen3_field>": [<filed_content>,...]}}, ...}

    **search(parameter)**: 
    - string content
    """
    p.update_pagination_item(item, search)
    results = p.get_pagination_data(item)
    query_count_total, query_match_pair, query_private_only = p.get_pagination_count(results["count_public"], results["count_private"])
    query_result = p.update_pagination_data(item, query_count_total, query_match_pair, query_private_only, results["public"])
    if item.search != {}:
        # Sort only if search is not empty, since search results are sorted by word relevance
        query_result = sorted(query_result, key=lambda dict: item.filter["submitter_id"].index(dict["submitter_id"]))
    result = {
        "items": p.reconstruct_data_structure(query_result),
        "numberPerPage": item.limit,
        "page": item.page,
        "total": query_count_total
    }
    return result


@ app.post("/filter/", tags=["Gen3"], summary="Get filter information", responses=filter_responses)
async def ger_filter(sidebar: bool, item: AccessItem):
    """
    /filter/?sidebar=<boolean>

    Return the support data for portal filters component.

    - **sidebar**: boolean content.
    """
    retry = 0
    # Stop waiting for the filter generator after hitting the retry limits
    # The retry limit here may need to be increased if there is a large database
    # This also depends on how fast the filter will be generated
    while retry < 12 and not FILTER_GENERATED:
        retry += 1
        time.sleep(retry)
    if FILTER_GENERATED:
        extra_filter = fg.generate_extra_filter(item.access)
        if sidebar == True:
            return f.generate_sidebar_filter_information(extra_filter)
        return f.generate_filter_information(extra_filter)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Failed to generate filter or the maximum retry limit was reached")


@ app.get("/metadata/download/{program}/{project}/{uuid}/{format}", tags=["Gen3"], summary="Download gen3 record information", response_description="Successfully return a JSON or CSV file contains the metadata")
async def download_gen3_metadata_file(program: str, project: str, uuid: str, format: FormatParam):
    """
    Return a single metadata file for a given uuid.

    - **program**: program name.
    - **project**: project name.
    - **uuid**: uuid of the file.
    - **format**: file format (must be one of the following: json, tsv).
    """
    try:
        metadata = SUBMISSION.export_record(program, project, uuid, format)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if "message" in metadata:
        if "unauthorized" in metadata["message"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=metadata["message"])
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=metadata["message"]+" and check if the correct project or uuid is used")
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


############################################
### iRODS                                ###
### Integrated Rule-Oriented Data System ###
############################################


def check_irods_status():
    try:
        SESSION.collections.get(iRODSConfig.IRODS_ENDPOINT_URL)
        return True
    except Exception:
        return False


def generate_collection_list(data):
    collection_list = []
    for ele in data:
        collection_list.append({
            "name": ele.name,
            "path": re.sub(iRODSConfig.IRODS_ENDPOINT_URL, '', ele.path)
        })
    return collection_list


@ app.post("/collection", tags=["iRODS"], summary="Get folder information", responses=sub_responses)
async def get_irods_collection(item: CollectionItem, connect: bool = Depends(check_irods_status)):
    """
    Return all collections from the required folder.

    Root folder will be returned if no item or "/" is passed.
    """
    if not SESSION_CONNECTED or not connect:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the irods server status or environment variables")

    if not re.match("(/(.)*)+", item.path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid path format is used")

    try:
        collect = SESSION.collections.get(
            iRODSConfig.IRODS_ENDPOINT_URL + item.path)
        folder_list = generate_collection_list(collect.subcollections)
        file_list = generate_collection_list(collect.data_objects)
        result = {
            "folders": folder_list,
            "files": file_list
        }
        return result
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Data not found in the provided path")


@ app.get("/data/{action}/{filepath:path}", tags=["iRODS"], summary="Download irods file", response_description="Successfully return a file with data")
async def get_irods_data_file(action: ActionParam, filepath: str, connect: bool = Depends(check_irods_status)):
    """
    Used to preview most types of data files in iRODS (.xlsx and .csv not supported yet).
    OR
    Return a specific download file from iRODS or a preview of most types data.

    - **action**: Action should be either preview or download.
    - **filepath**: Required iRODS file path.
    """
    if not SESSION_CONNECTED or not connect:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the irods server status or environment variables")

    chunk_size = 1024*1024*1024
    try:
        file = SESSION.data_objects.get(
            f"{iRODSConfig.IRODS_ENDPOINT_URL}/{filepath}")
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
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
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="The action is not provided in this API")

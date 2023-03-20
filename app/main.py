import mimetypes
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse, Response
from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission
from irods.session import iRODSSession

from app.config import Config, Gen3Config, iRODSConfig
from app.data_schema import *
from app.sgqlc import SimpleGraphQLClient
from app.filter import Filter
from app.pagination import Pagination

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

SUBMISSION = None
SESSION = None

sgqlc = SimpleGraphQLClient()
f = Filter()
p = Pagination()


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


#########################
### Gen3              ###
### Gen3 Data Commons ###
#########################


def get_name_list(data, name, path):
    name_dict = {name: []}
    for ele in data["links"]:
        name_dict[name].append(ele.replace(path, ""))
    return name_dict


@ app.get("/program", tags=["Gen3"], summary="Get gen3 program information", response_description="Gen3 program name")
async def get_gen3_program():
    """
    Return all programs information from the Gen3 Data Commons.
    """
    try:
        program = SUBMISSION.get_programs()
        return get_name_list(program, "program", "/v0/submission/")
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


@ app.get("/project/{program}", tags=["Gen3"], summary="Get gen3 project information", response_description="Gen3 project name")
async def get_gen3_project(program: ProgramParam):
    """
    Return all projects information from a gen3 program.

    - **program**: Gen3 program name.
    """
    try:
        project = SUBMISSION.get_projects(program)
        return get_name_list(project, "project", f"/v0/submission/{program}/")
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))


@ app.post("/dictionary", tags=["Gen3"], summary="Get gen3 dictionary information", response_description="Gen3 dictionary name")
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
        return get_name_list(dictionary, "dictionary", f"/v0/submission/{item.program}/{item.project}/_dictionary/")
    except Exception:
        raise HTTPException(
            status_code=NOT_FOUND, detail=f"Program {item.program} or project {item.project} not found")


@ app.post("/records/{node}", tags=["Gen3"], summary="Get gen3 node records information", response_description="A list of json object contains all records metadata within a node")
async def get_gen3_node_records(node: NodeParam, item: Gen3Item):
    """
    Return all records information in a dictionary node.

    - **node**: The dictionary node to export.
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


@ app.post("/record/{uuid}", tags=["Gen3"], summary="Get gen3 record information", response_description="A json object contains gen3 record metadata")
async def get_gen3_record(uuid: str, item: Gen3Item):
    """
    Return record information in the Gen3 Data Commons.

    - **uuid**: uuid of the record.
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


@ app.post("/graphql/query", tags=["Gen3"], summary="GraphQL query gen3 information")
async def graphql_query(item: GraphQLQueryItem):
    """
    Return queries metadata records. The API uses GraphQL query language.

    **filter**
    - {"<filed_name>": ["<attribute_name>", ...], ...}

    **search**
    - string content,
    - only available in manifest/case nodes
    """
    query_result = sgqlc.get_queried_result(item, SUBMISSION)
    return query_result[item.node]


@ app.post("/graphql/pagination/", tags=["Gen3"], summary="Display datasets", response_description="A list of datasets")
async def graphql_pagination(item: GraphQLPaginationItem, search: str = ""):
    """
    /graphql/pagination/?search=<string>

    Return filtered/searched metadata records. The API uses GraphQL query language.

    - Default page = 1
    - Default limit = 50
    - Default filter = {}
    - Default search = ""
    - Default relation = "and"

    filter post format should looks like: 
    {"id": {"node": "<gen3_node>", "filter": {"<gen3_field>": [<filed_content>,...]}}, ...}

    - **search**: string content.
    """
    p.update_pagination_item(item, search, SUBMISSION, SESSION)
    query_result = sgqlc.get_queried_result(item, SUBMISSION)
    if item.search != {}:
        # Sort only if search is not empty, since search results are sorted by word relevance
        query_result[item.node] = sorted(
            query_result[item.node], key=lambda dict: item.filter["submitter_id"].index(dict["submitter_id"]))
    return {
        "items": p.update_pagination_output(query_result[item.node]),
        # Maximum number of records display in one page
        "numberPerPage": item.limit,
        "page": item.page,
        "total": query_result["total"]
    }


@ app.get("/filter/", tags=["Gen3"], summary="Get filter information")
async def generate_filter(sidebar: bool):
    """
    /filter/?sidebar=<boolean>

    Return the support data for portal filters component.

    - **sidebar**: boolean content.
    """
    if sidebar == True:
        return f.generate_sidebar_filter_information()
    return f.generate_filter_information()


@ app.get("/metadata/download/{program}/{project}/{uuid}/{format}", tags=["Gen3"], summary="Download gen3 record information", response_description="A JSON or CSV file contains the metadata")
async def download_gen3_metadata_file(program: ProgramParam, project: ProjectParam, uuid: str, format: FormatParam):
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


############################################
### iRODS                                ###
### Integrated Rule-Oriented Data System ###
############################################


def get_collection_list(data):
    collect_list = []
    for ele in data:
        collect_list.append({
            "name": ele.name,
            "path": ele.path
        })
    return collect_list


@ app.get("/collection/root", tags=["iRODS"], summary="Get root information", response_description="All folders/files name and path under root folder")
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


@ app.post("/collection", tags=["iRODS"], summary="Get folder information", response_description="All folders/files name and path under selected folder")
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


@ app.get("/data/{action}/{filepath:path}", tags=["iRODS"], summary="Download irods file", response_description="A file with data")
async def get_irods_data_file(action: ActionParam, filepath: str):
    """
    Used to preview most types of data files in iRODS (.xlsx and .csv not supported yet).
    OR
    Return a specific download file from iRODS or a preview of most types data.

    - **action**: Action should be either preview or download.
    - **filepath**: Required iRODS file path.
    """
    chunk_size = 1024*1024*1024
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

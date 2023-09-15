import io
import re
import time
import mimetypes

from fastapi_utils.tasks import repeat_every
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse, Response
from pyorthanc import find

from app.config import iRODSConfig
from app.data_schema import *
from app.external_service import ExternalService
from app.filter_generator import FilterGenerator
from app.filter import Filter
from app.pagination_format import PaginationFormat
from app.pagination import Pagination
from app.query_format import QueryFormat
from app.search import Search
from app.sgqlc import SimpleGraphQLClient
from middleware.auth import Authenticator

app = FastAPI(
    title=title,
    description=description,
    # version="",
    # terms_of_service="",
    contact=contact,
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

es = ExternalService()
FILTER_GENERATED = False
fg = None
f = Filter()
pf = None
p = None
qf = None
sgqlc = None
a = Authenticator()


@ app.on_event("startup")
async def start_up():
    services = es.check_service_status()

    global sgqlc, fg, pf, p, qf
    sgqlc = SimpleGraphQLClient(services)
    fg = FilterGenerator(sgqlc)
    pf = PaginationFormat(fg)
    p = Pagination(fg, f, Search(services), sgqlc)
    qf = QueryFormat(fg, f)


@ app.on_event("startup")
@repeat_every(seconds=60*60*24)
def periodic_execution():
    global FILTER_GENERATED
    FILTER_GENERATED = False
    while not FILTER_GENERATED:
        FILTER_GENERATED = fg.generate_filter_dictionary()
        if FILTER_GENERATED:
            print("Default filter dictionary has been updated.")

    a.cleanup_authorized_user()


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


@ app.post("/access/token", tags=["Access"], summary="Create gen3 access token for authorized user", responses=access_token_responses)
async def create_gen3_access(item: IdentityItem, service: dict = Depends(es.check_service_status)):
    if service["gen3"] is None or service["irods"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (Gen3/iRODS) status")
    if item.identity == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing field in the request body")

    result = {
        "identity": item.identity,
        "access_token": a.generate_access_token(item.identity, service["gen3"], service["irods"])
    }
    return result


@ app.delete("/access/revoke", tags=["Access"], summary="Revoke gen3 access for authorized user", responses=access_revoke_responses)
async def revoke_gen3_access(is_revoked: bool = Depends(a.revoke_user_authority)):
    if is_revoked:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail="Revoke access successfully")


@ app.post("/dictionary", tags=["Gen3"], summary="Get gen3 dictionary information", responses=dictionary_responses)
async def get_gen3_dictionary(access_scope: list = Depends(a.gain_user_authority), service: dict = Depends(es.check_service_status)):
    """
    Return all dictionary nodes from the Gen3 Data Commons
    """
    if service["gen3"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (Gen3) status")
    
    program, project = split_access(access_scope)
    dictionary = service["gen3"].get_project_dictionary(program, project)
    dictionary_list = {"dictionary": []}
    for ele in dictionary["links"]:
        ele = ele.replace(
            f"/v0/submission/{program}/{project}/_dictionary/", "")
        dictionary_list["dictionary"].append(ele)
    return dictionary_list


@ app.get("/record/{uuid}", tags=["Gen3"], summary="Get gen3 record information", responses=record_responses)
async def get_gen3_record(uuid: str, access_scope: list = Depends(a.gain_user_authority), service: dict = Depends(es.check_service_status)):
    """
    Return record information in the Gen3 Data Commons.

    - **uuid**: uuid of the record.
    """
    if service["gen3"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (Gen3) status")

    program, project = split_access(access_scope)
    record = service["gen3"].export_record(program, project, uuid, "json")
    if "message" in record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=record["message"]+" and check if the correct project or uuid is used")

    result = {
        "record": record[0]
    }
    return result


@ app.post("/graphql/query", tags=["Gen3"], summary="GraphQL query gen3 metadata information", responses=query_responses)
async def get_gen3_graphql_query(item: GraphQLQueryItem, access_scope: list = Depends(a.gain_user_authority), service: dict = Depends(es.check_service_status)):
    """
    Return queries metadata records. The API uses GraphQL query language.

    **node**
    - experiment_query
    - dataset_description_query
    - manifest_query
    - case_query

    **filter**
    - {"field_name": ["field_value", ...], ...}

    **search**
    - string content,
    - only available in dataset_description/manifest/case nodes
    """
    if service["gen3"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (Gen3) status")
    
    item.access = access_scope
    query_result = sgqlc.get_queried_result(item)
    result = {
        "data": query_result[item.node],
    }
    # When use experiment_query to query specific dataset
    # Add related facets
    if "submitter_id" in item.filter and len(item.filter["submitter_id"]) == 1:
        data = query_result[item.node][0]
        result = {
            "data": qf.modify_output_data(data),
            "facets": qf.generate_related_facet(data)
        }
    return result


@ app.post("/graphql/pagination/", tags=["Gen3"], summary="Display datasets", responses=pagination_responses)
async def get_gen3_graphql_pagination(item: GraphQLPaginationItem, search: str = "", access_scope: list = Depends(a.gain_user_authority), service: dict = Depends(es.check_service_status)):
    """
    /graphql/pagination/?search=<string>

    Return filtered/searched metadata records. The API uses GraphQL query language.

    - Default page = 1
    - Default limit = 50
    - Default filter = {}
    - Default search = ""
    - Default relation = "and"
    - Default access = gen3 public access repository
    - Default order = "published(asc)"

    **node**
    - experiment_pagination

    **filter(zero or more)** 
    - {"gen3_node>gen3_field": [filter_name,...], ...}

    **search(parameter)**: 
    - string content
    """
    if service["gen3"] is None or service["irods"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (Gen3/iRODS) status")
    
    is_public_access_filtered = p.update_pagination_item(
        item, search, access_scope)
    data_count, match_pair = p.get_pagination_count(item)
    query_result = p.get_pagination_data(
        item, match_pair, is_public_access_filtered)
    # If both asc and desc are None, datasets ordered by self-written order function
    if item.asc == None and item.desc == None:
        query_result = sorted(
            query_result, key=lambda dict: item.filter["submitter_id"].index(dict["submitter_id"]))
    result = {
        "items": pf.reconstruct_data_structure(query_result),
        "numberPerPage": item.limit,
        "total": data_count
    }
    return result


@ app.get("/filter/", tags=["Gen3"], summary="Get filter information", responses=filter_responses)
async def get_gen3_filter(sidebar: bool, access_scope: list = Depends(a.gain_user_authority)):
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
    if not FILTER_GENERATED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Failed to generate filter or the maximum retry limit was reached")

    if sidebar == True:
        return fg.generate_sidebar_filter_information(access_scope)
    else:
        return fg.generate_filter_information(access_scope)


@ app.get("/metadata/download/{uuid}/{format}", tags=["Gen3"], summary="Download gen3 record information", response_description="Successfully return a JSON or CSV file contains the metadata")
async def get_gen3_metadata_file(uuid: str, format: FormatParam, access_scope: list = Depends(a.gain_user_authority), service: dict = Depends(es.check_service_status)):
    """
    Return a single metadata file for a given uuid.

    - **uuid**: uuid of the file.
    - **format**: file format (must be one of the following: json, tsv).
    """
    if service["gen3"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (Gen3) status")
    
    program, project = split_access(access_scope)
    try:
        metadata = service["gen3"].export_record(program, project, uuid, format)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if "message" in metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{metadata['message']} and check if the correct project or uuid is used")

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


@ app.post("/collection", tags=["iRODS"], summary="Get folder information", responses=collection_responses)
async def get_irods_collection(item: CollectionItem, service: dict = Depends(es.check_service_status)):
    """
    Return all collections from the required folder.

    Root folder will be returned if no item or "/" is passed.
    """
    if service["irods"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (iRODS) status")
    if not re.match("(/(.)*)+", item.path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid path format is used")

    def handle_collection(data):
        collection = []
        for ele in data:
            collection.append({
                "name": ele.name,
                "path": re.sub(iRODSConfig.IRODS_ROOT_PATH, '', ele.path)
            })
        return collection
    try:
        collect = service["irods"].collections.get(
            iRODSConfig.IRODS_ROOT_PATH + item.path)
        folder = handle_collection(collect.subcollections)
        file = handle_collection(collect.data_objects)
        result = {
            "folders": folder,
            "files": file
        }
        return result
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Data not found in the provided path")


@ app.get("/data/{action}/{filepath:path}", tags=["iRODS"], summary="Download irods file", response_description="Successfully return a file with data")
async def get_irods_data_file(action: ActionParam, filepath: str, service: dict = Depends(es.check_service_status)):
    """
    Used to preview most types of data files in iRODS (.xlsx and .csv not supported yet).
    OR
    Return a specific download file from iRODS or a preview of most types data.

    - **action**: Action should be either preview or download.
    - **filepath**: Required iRODS file path.
    """
    chunk_size = 1024*1024*1024

    if service["irods"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (iRODS) status")
    if action != "preview" and action != "download":
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="The action is not provided in this API")

    try:
        file = service["irods"].data_objects.get(
            f"{iRODSConfig.IRODS_ROOT_PATH}/{filepath}")
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Data not found in the provided path")

    def handle_header():
        header = None
        if action == "download":
            header = {"Content-Disposition": f"attachment;filename={file.name}"}
        return header

    def handle_mimetype():
        return mimetypes.guess_type(file.name)[0]

    def iterate_file():
        with file.open("r") as file_like:
            chunk = file_like.read(chunk_size)
            while chunk:
                yield chunk
                chunk = file_like.read(chunk_size)
    return StreamingResponse(iterate_file(), media_type=handle_mimetype(), headers=handle_header())


####################
### Orthanc      ###
### DICOM server ###
####################


@ app.post("/instance", tags=["Orthanc"], summary="Get instance ids", responses=instance_responses)
async def get_orthanc_instance(item: InstanceItem, service: dict = Depends(es.check_service_status)):
    if service["orthanc"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Please check the service (Orthanc) status")
    if item.study == None or item.series == None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing one or more fields in the request body")

    try:
        patients = find(
            orthanc=service["orthanc"],
            study_filter=lambda s: s.uid == item.study,
            series_filter=lambda s: s.uid == item.series,
        )
    except Exception as e:
        if "401" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid orthanc username or password are used")
    if patients == []:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource is not found in the orthanc server")

    instance_ids = []
    for patient in patients:
        for study in patient.studies:
            for series in study.series:
                for instance in series.instances:
                    instance_ids.append(instance.id_)
    return instance_ids


@ app.get("/dicom/export/{identifier}", tags=["Orthanc"], summary="Export dicom file", response_description="Successfully return a file with data")
async def get_orthanc_dicom_file(identifier: str, service: dict = Depends(es.check_service_status)):
    if service["orthanc"] is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Please check the service (Orthanc) status")
    
    try:
        instance_file = service["orthanc"].get_instances_id_file(identifier)
        bytes_file = io.BytesIO(instance_file)
        return Response(bytes_file.getvalue(), media_type="application/dicom")
    except Exception as e:
        if "401" in str(e):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid orthanc username or password are used")
        elif "404" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Resource is not found in the orthanc server")

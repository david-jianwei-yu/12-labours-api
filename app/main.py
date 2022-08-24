import json
import requests
import gspread

from typing import Union

from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse
from pydantic import BaseModel
from oauth2client.service_account import ServiceAccountCredentials

from app.config import Config, SpreadSheetConfig, Gen3Config
from app.dbtable import StateTable

app = FastAPI()

#Cross orgins, allow any for now
origins = [
    '*',
]

#Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

statetable = None

#CORS(app)

BAD_REQUEST = 400
NOT_FOUND = 404

SPREADSHEET_CREDENTIALS = {
    "type": SpreadSheetConfig.SHEET_TYPE,
    "project_id": SpreadSheetConfig.SHEET_PROJECT_ID,
    "private_key_id": SpreadSheetConfig.SHEET_PRIVATE_KEY_ID,
    "private_key": SpreadSheetConfig.SHEET_PRIVATE_KEY.replace("\\n", "\n"),
    "client_email": SpreadSheetConfig.SHEET_CLIENT_EMAIL,
    "client_id": SpreadSheetConfig.SHEET_CLIENT_ID,
    "auth_uri": SpreadSheetConfig.SHEET_AUTH_URI,
    "token_uri": SpreadSheetConfig.SHEET_TOKEN_URI,
    "auth_provider_x509_cert_url": SpreadSheetConfig.SHEET_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": SpreadSheetConfig.SHEET_CLIENT_X509_CERT_URL
}

GEN3_CREDENTIALS = {
    "api_key": Gen3Config.GEN3_API_KEY,
    "key_id": Gen3Config.GEN3_KEY_ID
}

HEADER = None

class ProgramItem(BaseModel):
    program: Union[str, None] = None
    project: Union[str, None] = None
    format: Union[str, None] = None

class GraphQLItem(BaseModel):
    node_type: Union[str, None] = None
    # Condition post format should looks like
    # '(project_id: ["demo1-jenkins", ...], tissue_type: ["Contrived", "Normal", ...], ...)'
    condition: Union[str, None] = None
    # Field post format should looks like
    # "submitter_id tissue_type tumor_code ..."
    field: Union[str, None] = None

@app.on_event("startup")
async def start_up():
    try:
        global statetable
        statetable = StateTable(Config.DATABASE_URL)
    except AttributeError:
        print("Encoutner an error setting up the database")
        statetable = None

    try:
        global HEADER
        TOKEN = requests.post(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/user/credentials/cdis/access_token", json=GEN3_CREDENTIALS).json()
        HEADER = {"Authorization": "bearer " + TOKEN["access_token"]}
    except Exception:
        print("Encoutner an error while generating a token from GEN3")


@app.get("/", response_class=PlainTextResponse)
async def root():
    return "This is the fastapi backend."


@app.get("/health", response_class=PlainTextResponse)
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
@app.put("/state/getshareid")
async def get_share_link():
    return get_share_link(statetable)


# Get the map state using the share link id.
@app.get("/state/getstate")
async def get_state():
    return get_saved_state(statetable)


@app.get("/spreadsheet")
# Connect to the google spreadsheet and get all spreadsheet data.
async def spreadsheet():
    scope = [
        "https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"
    ]
    credential = ServiceAccountCredentials.from_json_keyfile_dict(
        SPREADSHEET_CREDENTIALS, scope)
    client = gspread.authorize(credential)
    gsheet = client.open("organ_sheets").sheet1
    data = gsheet.get_all_records()
    return data


@app.get("/program")
# Get the program information from Gen3 Data Commons
async def program():
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


@app.get("/projects/{program}")
# Get all projects information from Gen3 Data Commons
def project(program: str):
    if program == None:
        raise HTTPException(status_code=BAD_REQUEST, detail="Missing request")

    res = requests.get(
        f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{program}", headers=HEADER)
    try:
        res.raise_for_status()
        json_data = json.loads(res.content)
        project_list = []
        for ele in json_data["links"]:
            project_list.append(ele.replace(
                f"/v0/submission/{program}/", ""))
        new_json_data = {"project": project_list}
        return new_json_data
    except Exception as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))


@app.get("/dictionary")
# Get all dictionary node from Gen3 Data Commons
def dictionary():
    res = requests.get(
        f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/_dictionary", headers=HEADER)
    try:
        res.raise_for_status()
        json_data = json.loads(res.content)
        dictionary_list = []
        for ele in json_data["links"]:
            dictionary_list.append(ele.replace(
                "/v0/submission/_dictionary/", ""))
        new_json_data = {"dictionary": dictionary_list}
        return new_json_data
    except Exception as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))


def is_json(json_data):
    try:
        json.loads(json_data)
    except ValueError:
        return False
    return True

@app.post("/nodes/{node_type}")
# Exports all records in a dictionary node
def export_node(node_type: str, item: ProgramItem):
    if item.program == None or item.project == None or item.format == None:
        raise HTTPException(status_code=BAD_REQUEST, detail="Missing one ore more fields in request body")

    res = requests.get(
        f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{item.program}/{item.project}/export/?node_label={node_type}&format={item.format}", headers=HEADER)
    try:
        res.raise_for_status()
        json_data = json.loads(res.content)
        if is_json(res.content) and "data" in json_data and json_data["data"] != []:
            return res.content
        else:
            raise HTTPException(status_code=NOT_FOUND, detail="Records cannot be found")
    except Exception as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))

@app.post("/records/{uuids}")
# Exports one or more records(records must in one node), use comma to separate the uuids
# e.g. uuid1,uuid2,uuid3
def export_record(uuids: str, item: ProgramItem):
    if item.program == None or item.project == None or item.format == None:
        raise HTTPException(status_code=BAD_REQUEST, detail="Missing one ore more fields in request body")

    res = requests.get(
        f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{item.program}/{item.project}/export/?ids={uuids}&format={item.format}", headers=HEADER)
    try:
        res.raise_for_status()
        json_data = json.loads(res.content)
        if b"id" in res.content:
            return res.content
        else:
            raise HTTPException(status_code=NOT_FOUND, detail=json_data["message"])
    except Exception as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))

@app.post("/graphql")
# Only used for filtering the files in a specific node for now
def graphql_filter(item: GraphQLItem):
    if item.node_type == None or item.condition == None or item.field == None:
        raise HTTPException(status_code=BAD_REQUEST, detail="Missing one ore more fields in request body")

    query = {
        "query":
        """{""" +
        f"""{item.node_type}{item.condition}""" +
        """{""" +
        f"""{item.field}""" +
        """}""" +
        """}"""
    }

    res = requests.post(
        f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/graphql/", json=query, headers=HEADER)

    try:
        res.raise_for_status()
        json_data = json.loads(res.content)
        if json_data["data"] == None:
            raise HTTPException(status_code=NOT_FOUND, detail=json_data["errors"])
        else:
            if json_data["data"][f"{node_type}"] == []:
                raise HTTPException(status_code=NOT_FOUND, detail="Data cannot be found for node_type")
            else:
                return res.content
    except Exception as e:
        raise HTTPException(status_code=res.status_code, detail=str(e))

@app.get("/download/metadata/{program}/{project}/{uuid}/{format}/{filename}")
def download_gen3_metadata_file(program: str, project: str, uuid: str, format: str, filename:str):
    try:
        res = requests.get(
            f"{Gen3Config.GEN3_ENDPOINT_URL}/api/v0/submission/{program}/{project}/export/?ids={uuid}&format={format}", headers=HEADER)
        res.raise_for_status()
        if format == "json":
            return Response(content=res.content,
                            media_type="application/json",
                            headers={"Content-Disposition":
                                     f"attachment;filename={filename}.json"})
        else:
            return Response(content=res.content,
                            media_type="text/csv",
                            headers={"Content-Disposition":
                                     f"attachment;filename={filename}.csv"})
    except Exception as e:
        raise HTTPException(status_code=NOT_FOUND, detail=str(e))

"""
Functionality for processing gen3 service
- process_graphql_query
- process_program_project -> temp
- get
- status
- connect
"""
import re
import time

from fastapi import HTTPException, status
from gen3.auth import Gen3Auth, Gen3AuthError
from gen3.submission import Gen3Submission

from app.config import Gen3Config


class Gen3Service:
    """
    Gen3 service functionality
    sgqlc -> simple graphql client object is required
    """

    def __init__(self, sgqlc):
        self._sgqlc = sgqlc
        self.__submission = None
        self.__retry = 0

    def process_graphql_query(self, item, key=None, queue=None):
        """
        Handler for fetching gen3 data with graphql query code
        """
        if item.node is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing field in the request body",
            )

        query_code = self._sgqlc.handle_graphql_query_code(item)
        try:
            query_result = self.__submission.query(query_code)["data"][item.node]
            if key is not None and queue is not None:
                queue.put({key: query_result})
            return query_result
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            ) from error

    def process_program_project(self, policies):
        """
        Handler for processing gen3 program/project name
        Temporary function
        """

        def handle_name(data, type_name=None):
            name_list = []
            for _ in data["links"]:
                name = _.replace("/v0/submission/", "")
                if type_name == "hyphen":
                    name = re.sub("/", "-", name)
                name_list.append(name)
            return name_list

        try:
            program_list = handle_name(self.__submission.get_programs())
            project = {"links": []}
            for program in list(set(policies).intersection(program_list)):
                project["links"] += handle_name(self.__submission.get_projects(program))
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            ) from error

        return handle_name(project, "hyphen")

    def get(self):
        """
        Handler for getting gen3 submission
        """
        return self.__submission

    def status(self):
        """
        Handler for checking gen3 connection status
        """
        try:
            self.__submission.get_programs()
            self.__retry = 0
        except Gen3AuthError:
            print("Gen3 disconnected.")
            self.__submission = None
            if self.__retry == 12:
                print("Hit the max retry limit.")
            if self.__retry < 12:
                self.__retry += 1
                print(f"Reconnecting...{self.__retry}...")
                time.sleep(self.__retry)
                self.connect()

    def connect(self):
        """
        Handler for connecting gen3 service
        """
        try:
            self.__submission = Gen3Submission(
                Gen3Auth(
                    endpoint=Gen3Config.GEN3_ENDPOINT_URL,
                    refresh_token={
                        "api_key": Gen3Config.GEN3_API_KEY,
                        "key_id": Gen3Config.GEN3_KEY_ID,
                    },
                )
            )
            self.status()
        except Exception:
            print("Failed to create the Gen3 submission.")

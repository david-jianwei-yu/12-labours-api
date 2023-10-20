"""
Functionality for processing gen3 service
- process_graphql_query
- process_program_project -> temp
- get_status
- status
- get_connection
- connection
"""
import logging
import re
import time

from fastapi import HTTPException, status
from gen3.auth import Gen3Auth, Gen3AuthError
from gen3.submission import Gen3Submission

from app.config import Gen3Config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Gen3Service:
    """
    Gen3 service functionality
    sgqlc -> simple graphql client object is required
    """

    def __init__(self, sgqlc):
        self.__sgqlc = sgqlc
        self.__submission = None
        self.__status = False
        self.__retry = 0

    def process_graphql_query(self, item, key=None, queue=None):
        """
        Handler for fetching gen3 data with graphql query code
        """
        try:
            query_code = self.__sgqlc.handle_graphql_query_code(item)
            query_result = self.__submission.query(query_code)["data"][item.node]
            if key is not None and queue is not None:
                queue.put({key: query_result})
            return query_result
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            ) from error

    def process_program_project(self, policies=None):
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
            if policies:
                program_list = list(set(policies).intersection(program_list))
            for program in program_list:
                project["links"] += handle_name(self.__submission.get_projects(program))
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            ) from error

        return handle_name(project, "hyphen")

    def get_status(self):
        """
        Handler for getting gen3 submission status
        """
        return self.__status

    def status(self):
        """
        Handler for checking gen3 submission status
        """
        try:
            self.__submission.get_programs()
            self.__status = True
            self.__retry = 0
        except Gen3AuthError as error:
            logger.warning("Gen3 disconnected.")
            self.__submission = None
            self.__status = False
            if self.__retry == 12:
                logger.error("Hit the max retry limit. Unable to reconnect.")
                logger.error(error)
            if self.__retry < 12:
                self.__retry += 1
                logger.warning("Reconnecting...%s...", self.__retry)
                time.sleep(self.__retry)
                self.connection()

    def get_connection(self):
        """
        Handler for getting gen3 submission service
        """
        return self.__submission

    def connection(self):
        """
        Handler for connecting gen3 submission service
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
            logger.error("Failed to create the Gen3 submission.")

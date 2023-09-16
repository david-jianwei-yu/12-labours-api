import time
from fastapi import HTTPException, status

from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission
from irods.session import iRODSSession
from pyorthanc import Orthanc

from app.config import Gen3Config, OrthancConfig, iRODSConfig


class ExternalService:
    def __init__(self, sgqlc):
        self._sgqlc = sgqlc
        self.services = {"gen3": None, "irods": None, "orthanc": None}
        self.retry = 0

    def check_orthanc_status(self):
        try:
            self.services["orthanc"].get_patients()
        except Exception:
            print("Orthanc disconnected")
            self.services["orthanc"] = None

    def connect_to_orthanc(self):
        try:
            self.services["orthanc"] = Orthanc(
                OrthancConfig.ORTHANC_ENDPOINT_URL,
                username=OrthancConfig.ORTHANC_USERNAME,
                password=OrthancConfig.ORTHANC_PASSWORD,
            )
            self.check_orthanc_status()
        except Exception:
            print("Failed to create the Orthanc client.")

    def check_irods_status(self):
        try:
            self.services["irods"].collections.get(iRODSConfig.IRODS_ROOT_PATH)
        except Exception:
            print("iRODS disconnected")
            self.services["irods"] = None

    def connect_to_irods(self):
        try:
            # This function is used to connect to the iRODS server
            # It requires "host", "port", "user", "password" and "zone" environment variables.
            self.services["irods"] = iRODSSession(
                host=iRODSConfig.IRODS_HOST,
                port=iRODSConfig.IRODS_PORT,
                user=iRODSConfig.IRODS_USER,
                password=iRODSConfig.IRODS_PASSWORD,
                zone=iRODSConfig.IRODS_ZONE,
            )
            # self.services["irods"].connection_timeout =
            self.check_irods_status()
        except Exception:
            print("Failed to create the iRODS session.")

    def process_gen3_graphql_query(self, item, key=None, queue=None):
        """
        Handler for fetching gen3 data with graphql query code
        """
        if item.node is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing one or more fields in the request body",
            )

        query = self._sgqlc.handle_graphql_query_code(item)
        try:
            result = self.services["gen3"].query(query)["data"][item.node]
            if key is not None and queue is not None:
                queue.put({key: result})
            return result
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            ) from error

    def check_gen3_status(self):
        try:
            self.services["gen3"].get_programs()
            self.retry = 0
        except Exception:
            print("Gen3 disconnected")
            self.services["gen3"] = None
            if self.retry < 12:
                self.retry += 1
                print(f"Reconnecting...{self.retry}...")
                time.sleep(self.retry)
                self.connect_to_gen3()

    def connect_to_gen3(self):
        try:
            self.services["gen3"] = Gen3Submission(
                Gen3Auth(
                    endpoint=Gen3Config.GEN3_ENDPOINT_URL,
                    refresh_token={
                        "api_key": Gen3Config.GEN3_API_KEY,
                        "key_id": Gen3Config.GEN3_KEY_ID,
                    },
                )
            )
            self.check_gen3_status()
        except Exception:
            print("Failed to create the Gen3 submission.")

    def check_service_status(self):
        if self.services["gen3"] is None:
            self.connect_to_gen3()
        else:
            self.check_gen3_status()

        if self.services["irods"] is None:
            self.connect_to_irods()
        else:
            self.check_irods_status()

        if self.services["orthanc"] is None:
            self.connect_to_orthanc()
        else:
            self.check_orthanc_status()
        return self.services

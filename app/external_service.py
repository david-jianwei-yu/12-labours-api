import time

from gen3.auth import Gen3Auth
from gen3.submission import Gen3Submission
from irods.session import iRODSSession
from pyorthanc import Orthanc

from app.config import Gen3Config, OrthancConfig, iRODSConfig


class ExternalService:
    def __init__(self):
        self.services = {"gen3": None, "irods": None, "orthanc": None}
        self.retry = 0

    def check_orthanc_status(self):
        try:
            self.services["orthanc"].get_patients()
        except Exception:
            self.services["orthanc"] = None
            print("Orthanc disconnected")

    def connect_to_orthanc(self):
        try:
            self.services["orthanc"] = Orthanc(
                OrthancConfig.ORTHANC_ENDPOINT_URL,
                username=OrthancConfig.ORTHANC_USERNAME,
                password=OrthancConfig.ORTHANC_PASSWORD,
            )
            self.check_orthanc_status()
        except Exception:
            print("Encounter an error while creating the Orthanc client.")

    def check_irods_status(self):
        try:
            self.services["irods"].collections.get(iRODSConfig.IRODS_ROOT_PATH)
        except Exception:
            self.services["irods"] = None
            print("iRODS disconnected")

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
            print("Encounter an error while creating the iRODS session.")

    def check_gen3_status(self):
        try:
            self.services["gen3"].get_programs()
            self.retry = 0
        except Exception:
            self.services["gen3"] = None
            print("Gen3 disconnected")
            print(f"Reconnecting...{self.retry}...")
            if self.retry < 12:
                self.retry += 1
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
            print("Encounter an error while creating the GEN3 auth.")

    def check_service_status(self):
        if self.services["gen3"] is None:
            self.connect_to_gen3()
        if self.services["irods"] is None:
            self.connect_to_irods()
        if self.services["orthanc"] is None:
            self.connect_to_orthanc()
        return self.services

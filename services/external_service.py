"""
Functionality for using external service
- get
- check_service_status
"""

from services.gen3.gen3_service import Gen3Service
from services.gen3.sgqlc import SimpleGraphQLClient
from services.irods.irods_service import iRODSService
from services.orthanc.orthanc_service import OrthancService


class ExternalService:
    """
    External services functionality
    """

    def __init__(self):
        self.__services = {
            "gen3": {"object": Gen3Service(SimpleGraphQLClient()), "connection": None},
            "irods": {"object": iRODSService(), "connection": None},
            "orthanc": {"object": OrthancService(), "connection": None},
        }

    def get(self, service):
        """
        Handler for getting service object
        """
        return self.__services[service]["object"]

    def check_service_status(self):
        """
        Handler for checking external service status
        """
        connection = {}
        for name, service in self.__services.items():
            if service["connection"] is None:
                service["object"].connect()
                service["connection"] = service["object"].get()
            else:
                service["object"].status()
            connection[name] = service["connection"]
        return connection

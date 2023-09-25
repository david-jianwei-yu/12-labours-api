"""
Functionality for processing orthanc service
- get_status
- status
- get_connection
- connection
"""
import logging

from pyorthanc import Orthanc

from app.config import OrthancConfig

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OrthancService:
    """
    Orthanc service functionality
    """

    def __init__(self):
        self.__orthanc = None
        self.__status = False

    def get_status(self):
        """
        Handler for getting orthanc client status
        """
        return self.__status

    def status(self):
        """
        Handler for checking orthanc client status
        """
        try:
            self.__orthanc.get_patients()
            self.__status = True
        except Exception as error:
            logger.warning("Orthanc disconnected.")
            logger.error(error)
            self.__orthanc = None
            self.__status = False

    def get_connection(self):
        """
        Handler for getting orthanc client service
        """
        return self.__orthanc

    def connection(self):
        """
        Handler for connecting orthanc client service
        """
        try:
            self.__orthanc = Orthanc(
                OrthancConfig.ORTHANC_ENDPOINT_URL,
                username=OrthancConfig.ORTHANC_USERNAME,
                password=OrthancConfig.ORTHANC_PASSWORD,
            )
            self.status()
        except Exception:
            logger.error("Failed to create the Orthanc client.")

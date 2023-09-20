"""
Functionality for processing orthanc service
- get
- status
- connect
"""
from pyorthanc import Orthanc

from app.config import OrthancConfig


class OrthancService:
    """
    Orthanc service functionality
    """

    def __init__(self):
        self.__orthanc = None

    def get(self):
        """
        Handler for getting orthanc
        """
        return self.__orthanc

    def status(self):
        """
        Handler for checking orthanc connection status
        """
        try:
            self.__orthanc.get_patients()
        except Exception:
            print("Orthanc disconnected.")
            self.__orthanc = None

    def connect(self):
        """
        Handler for connecting orthanc service
        """
        try:
            self.__orthanc = Orthanc(
                OrthancConfig.ORTHANC_ENDPOINT_URL,
                username=OrthancConfig.ORTHANC_USERNAME,
                password=OrthancConfig.ORTHANC_PASSWORD,
            )
            self.status()
        except Exception:
            print("Failed to create the Orthanc client.")

import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    JWT_SECURE_KEY = os.environ.get("JWT_SECURE_KEY")


class Gen3Config(object):
    GEN3_ENDPOINT_URL = os.environ.get("GEN3_ENDPOINT_URL")
    GEN3_API_KEY = os.environ.get("GEN3_API_KEY")
    GEN3_KEY_ID = os.environ.get("GEN3_KEY_ID")
    GEN3_PUBLIC_ACCESS = os.environ.get("GEN3_PUBLIC_ACCESS")


class iRODSConfig(object):
    IRODS_HOST = os.environ.get("IRODS_HOST")
    IRODS_PORT = os.environ.get("IRODS_PORT")
    IRODS_USER = os.environ.get("IRODS_USER")
    IRODS_PASSWORD = os.environ.get("IRODS_PASSWORD")
    IRODS_ZONE = os.environ.get("IRODS_ZONE")
    IRODS_ROOT_PATH = os.environ.get("IRODS_ROOT_PATH")


class OrthancConfig(object):
    ORTHANC_ENDPOINT_URL = os.environ.get("ORTHANC_ENDPOINT_URL")
    ORTHANC_USERNAME = os.environ.get("ORTHANC_USERNAME")
    ORTHANC_PASSWORD = os.environ.get("ORTHANC_PASSWORD")

import os
from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    BASE_URL = os.environ.get('BASE_URL')
    PORTAL_URL = os.environ.get('PORTAL_URL')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DEPLOY_ENV = os.environ.get("DEPLOY_ENV", "development")
    LABOURS_APP_HOST = os.environ.get("LABOURS_APP_HOST")


class Gen3Config(object):
    GEN3_ENDPOINT_URL = os.environ.get("GEN3_ENDPOINT_URL")
    GEN3_API_KEY = os.environ.get("GEN3_API_KEY")
    GEN3_KEY_ID = os.environ.get("GEN3_KEY_ID")


class iRODSConfig(object):
    IRODS_HOST = os.environ.get("IRODS_HOST")
    IRODS_PORT = os.environ.get("IRODS_PORT")
    IRODS_USER = os.environ.get("IRODS_USER")
    IRODS_PASSWORD = os.environ.get("IRODS_PASSWORD")
    IRODS_ZONE = os.environ.get("IRODS_ZONE")
    IRODS_ENDPOINT_URL = os.environ.get("IRODS_ENDPOINT_URL")

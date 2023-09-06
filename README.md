# 12-labours-api

Query API services for 12 Labours App

# Overview

This is the API service providing query and data requests for the 12 Labours projects. This is currently implemented using fastapi.

# Requirements

## Python 3.6 or above

Make sure you have python 3 installed `python3 --version`.

Python version `3.9.0` used for this project.

Pip version `20.3.1` used for this project.

## Environment variables

Here is the list of environment variables used by the app.

### For production:

Please fill in the environment variables in the `env.txt` file and rename the file name to `.env`.

### For deployment:

The environment variables template has been shown below:

```bash
JWT_SECURE_KEY =

GEN3_ENDPOINT_URL =
GEN3_API_KEY =
GEN3_KEY_ID =
GEN3_PUBLIC_ACCESS =

IRODS_ROOT_PATH =
IRODS_HOST =
IRODS_PASSWORD =
IRODS_PORT =
IRODS_USER =
IRODS_ZONE =
```

## Running the app

```bash
# Create the virtual environment
$ python3 -m venv ./venv
# Active the virtual environment
$ . ./venv/bin/activate
# Install all required dependencies
$ pip install -r requirements.txt
# Run the backend application
$ uvicorn main:app or uvicorn main:app --port <port number>
```

## Database

### `Gen3 Data Commons`

The connection between the backend and Gen3 Data Commons is directly through sending requests to Gen3 API. The backend will frequently request the access token to keep continuous interactions.

```bash
global SUBMISSION
GEN3_CREDENTIALS = {
    "api_key": Gen3Config.GEN3_API_KEY,
    "key_id": Gen3Config.GEN3_KEY_ID
}
AUTH = Gen3Auth(endpoint=Gen3Config.GEN3_ENDPOINT_URL,
                refresh_token=GEN3_CREDENTIALS)
SUBMISSION = Gen3Submission(AUTH)
```

More information about the usage of this database in [the documentation](https://gen3.org/resources/user/using-api/).

### `iRODS`

iRODS provides a Python package. Using the iRODSession to create the session to provide further features.

```bash
global SESSION
SESSION = iRODSSession(host=iRODSConfig.IRODS_HOST,
                        port=iRODSConfig.IRODS_PORT,
                        user=iRODSConfig.IRODS_USER,
                        password=iRODSConfig.IRODS_PASSWORD,
                        zone=iRODSConfig.IRODS_ZONE)
```

More information about the usage of this database in [the documentation](https://github.com/irods/python-irodsclient).

## Third-party packages

### `sgqlc`

This package offers an easy to use GraphQL client.

More information about the usage of this package in [the documentation](https://sgqlc.readthedocs.io/en/latest/).

# Testing

If you do not have the 12 Labours portal user environment variables setup already:

1. Fill in the `env.txt` file with the configuration variables of the 12 Labours portal user.
2. Rename the file name to `.env`.

After the previous steps or if you already have those environment variables setup, run:

(Optional) If the app has not been run before, you should run the following commands first:

```bash
# Create the virtual environment
$ python3 -m venv ./venv
# Active the virtual environment
$ . ./venv/bin/activate
# Install all required dependencies
$ pip install -r requirements.txt
```

Otherwise, you only need to run the following commands:

```bash
# Install required dependencies for testing
$ pip install -r requirements-dev.txt
# Set the python path to the current diectory
$ export PYTHONPATH=.
# Run the pytest
$ pytest --timeout=<time in second>
```

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
QUERY_SECURE_KEY =
QUERY_ACCESS_TOKEN =

GEN3_ENDPOINT_URL =
GEN3_API_KEY =
GEN3_KEY_ID =
GEN3_PUBLIC_ACCESS =

IRODS_HOST =
IRODS_PASSWORD =
IRODS_PORT =
IRODS_USER =
IRODS_ZONE =
IRODS_ROOT_PATH =

ORTHANC_ENDPOINT_URL =
ORTHANC_USERNAME =
ORTHANC_PASSWORD =
```

## Running the app

```bash
# Optional
$ pip install --upgrade pip
# Create the virtual environment
$ python3 -m venv ./venv
# Active the virtual environment
$ . ./venv/bin/activate
# Install all required dependencies
$ pip install -r requirements.txt
# Run the backend application, optional to use --port to run at specific port
$ uvicorn main:app (--port <port number>)
```

## Database

### `Gen3 Data Commons`

The connection between the backend and Gen3 Data Commons is directly through sending requests to Gen3 API. The backend will frequently request the access token to keep continuous interactions.

```bash
Gen3Submission(
    Gen3Auth(
        endpoint=Gen3Config.GEN3_ENDPOINT_URL,
        refresh_token={
            "api_key": Gen3Config.GEN3_API_KEY,
            "key_id": Gen3Config.GEN3_KEY_ID,
        },
    )
)
```

More information about the usage of this database in [the documentation](https://gen3.org/resources/user/using-api/).

### `iRODS`

iRODS provides Python SDK. Using the iRODSession to create the session to provide further features.

```bash
iRODSSession(
    host=iRODSConfig.IRODS_HOST,
    port=iRODSConfig.IRODS_PORT,
    user=iRODSConfig.IRODS_USER,
    password=iRODSConfig.IRODS_PASSWORD,
    zone=iRODSConfig.IRODS_ZONE,
)
```

### `Orthanc`

```bash
Orthanc(
    OrthancConfig.ORTHANC_ENDPOINT_URL,
    username=OrthancConfig.ORTHANC_USERNAME,
    password=OrthancConfig.ORTHANC_PASSWORD,
)
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
# Run the pytest, optional to use --timeout= to limit the time for each test case
$ pytest (--timeout=<time in second>)
```

# Developer Code Standards

Recommend to use following package to assist API development:

### `Black` - The Uncompromising Code Formatter

Black makes code review faster by producing the smallest diffs possible. Blackened code looks the same regardless of the project you’re reading. Formatting becomes transparent after a while and you can focus on the content instead.

For official documentation, click [here](https://black.readthedocs.io/en/stable/).

### `Pylint` - Static code analyser

Pylint analyses your code without actually running it. It checks for errors, enforces a coding standard, looks for code smells, and can make suggestions about how the code could be refactored.

For official documentation, click [here](https://pylint.readthedocs.io/en/stable/).

### `Mypy` - Optional static typing for Python

Mypy is essentially a Python linter on steroids, and it can catch many programming errors by analyzing your program, without actually having to run it. Mypy has a powerful type system with features such as type inference, gradual typing, generics and union types.

### `isort`

isort is a Python utility / library to sort imports alphabetically, and automatically separated into sections and by type.

For official documentation, click [here](https://pycqa.github.io/isort/).

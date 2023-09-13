"""
Functionality for backend services access control
- AUTHORIZED_USERS
- cleanup_authorized_user
- handle_revoke_authority
- handle_gain_authority
- generate_access_token
"""
import json
import re
from datetime import datetime
from multiprocessing import Manager

import yaml
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from yaml import SafeLoader

from app.config import Gen3Config, iRODSConfig
from middleware.jwt import JWT
from middleware.user import User

security = HTTPBearer()
manager = Manager()
jwt = JWT()

AUTHORIZED_USERS = manager.dict()


class Authenticator:
    """
    Authentication functionality
    """

    def __init__(self):
        AUTHORIZED_USERS["public"] = User(
            "public", [Gen3Config.GEN3_PUBLIC_ACCESS], None
        )

    def get_authorized_user_number(self):
        """
        Return the number of user in AUTHORIZED_USERS
        """
        return len(AUTHORIZED_USERS)

    def _delete_expired_user(self, user):
        """
        Handler for finding and deleting expired users from AUTHORIZED_USERS
        """
        if user in AUTHORIZED_USERS and user != "public":
            current_time = datetime.now()
            expire_time = AUTHORIZED_USERS[user].get_user_expire_time()
            if current_time >= expire_time:
                del AUTHORIZED_USERS[user]

    def cleanup_authorized_user(self):
        """
        Handler for providing deleting expired users option outside auth file
        """
        for user in list(AUTHORIZED_USERS):
            if user != "public":
                self._delete_expired_user(user)
        print("All expired users have been deleted.")

    def _handle_authenticate_token(self, token, auth_type=None):
        """
        Handler for verifying the authenticate token validity
        """
        try:
            if token == "undefined":
                return AUTHORIZED_USERS["public"]
            # Token will always be decoded
            decrypt_identity = jwt.decoding_token(token)["identity"]
            if auth_type is None:
                # Check and remove expired user
                # Currently should only for self.handle_gain_authority
                self._delete_expired_user(decrypt_identity)
            return AUTHORIZED_USERS[decrypt_identity]
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from error

    async def handle_revoke_authority(
        self, token: HTTPAuthorizationCredentials = Depends(security)
    ):
        """
        Handler for delete user access scope if token is valid
        """
        verify_user = self._handle_authenticate_token(token.credentials, "revoke")
        if verify_user.get_user_identity() == "public":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to remove default access authority",
            )

        del AUTHORIZED_USERS[verify_user.get_user_identity()]
        return True

    async def handle_gain_authority(
        self, token: HTTPAuthorizationCredentials = Depends(security)
    ):
        """
        Handler for returning user access scope if token is valid
        """
        verify_user = self._handle_authenticate_token(token.credentials)
        return verify_user.get_user_access_scope()

    def _handle_name(self, data, path, type_name=None):
        """
        Handler for processing gen3 program/project name
        """
        name_list = []
        for _ in data:
            name = _.replace(path, "")
            if type_name == "access":
                name = re.sub("/", "-", name)
            name_list.append(name)
        return name_list

    def _handle_access_scope(self, policies, SUBMISSION):
        """
        Handler for generating gen3 access scopes
        """
        try:
            program = SUBMISSION.get_programs()
            program_list = self._handle_name(program["links"], "/v0/submission/")
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
            ) from error

        project = {"links": []}
        for prog in list(set(policies).intersection(program_list)):
            project["links"] += SUBMISSION.get_projects(prog)["links"]
        return self._handle_name(project["links"], "/v0/submission/", "access")

    def _handle_user_authority(self, identity, user_yaml, SUBMISSION):
        """
        Handler for generating user authority object
        """
        email = identity.split(">")[0]
        expiration = identity.split(">")[2]
        if email in user_yaml and expiration != "false":
            # Avoid user object expired but not removed
            # Provide auto renew ability when user request access
            # Always return valid user object
            self._delete_expired_user(identity)
            if identity in AUTHORIZED_USERS:
                return AUTHORIZED_USERS[identity]
            policies = user_yaml[email]["policies"]
            scope = self._handle_access_scope(policies, SUBMISSION)
            expire_time = datetime.fromtimestamp(int(expiration) / 1000)
            user = User(identity, scope, expire_time)
            AUTHORIZED_USERS[identity] = user
            return user
        return AUTHORIZED_USERS["public"]

    def generate_access_token(self, identity, SUBMISSION, SESSION):
        """
        Handler for generating gen3 access_token to limit user access scope
        """
        try:
            yaml_string = ""
            user_obj = SESSION.data_objects.get(
                f"{iRODSConfig.IRODS_ROOT_PATH}/user.yaml"
            )
            with user_obj.open("r") as file:
                for line in file:
                    yaml_string += str(line, encoding="utf-8")
            user_yaml = json.loads(
                json.dumps(yaml.load(yaml_string, Loader=SafeLoader))
            )["users"]
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User data not found in the provided path",
            ) from error

        user = self._handle_user_authority(identity, user_yaml, SUBMISSION)
        access_token = jwt.encoding_token(
            {
                "identity": user.get_user_identity(),
                "scope": user.get_user_access_scope(),
            }
        )
        return access_token

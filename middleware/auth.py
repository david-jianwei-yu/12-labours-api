"""
Functionality for backend services access control
- AUTHORIZED_USERS
- get_authorized_user_number
- cleanup_authorized_user
- handle_revoke_authority
- handle_get_one_off_authority
- handle_get_authority
- generate_access_token
"""
import logging
from datetime import datetime, timedelta, timezone
from multiprocessing import Manager

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Config, Gen3Config
from middleware.jwt import JWT
from middleware.user import User

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

security = HTTPBearer()
manager = Manager()
jwt = JWT()

AUTHORIZED_USERS = manager.dict()


class Authenticator:
    """
    Authentication functionality
    """

    def __init__(self, es):
        self.__es = es
        self.__public = {
            "identity": "public",
            "token": Config.QUERY_ACCESS_TOKEN,
        }
        AUTHORIZED_USERS[self.__public["identity"]] = User(
            self.__public["identity"],
            [Gen3Config.GEN3_PUBLIC_ACCESS],
            None,
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
        if user in AUTHORIZED_USERS and user != self.__public["identity"]:
            current_time = datetime.now()
            expire_time = AUTHORIZED_USERS[user].get_user_expire_time()
            if current_time >= expire_time:
                del AUTHORIZED_USERS[user]

    def cleanup_authorized_user(self):
        """
        Handler for providing deleting expired users option outside auth file
        """
        for user in list(AUTHORIZED_USERS):
            if user != self.__public["identity"]:
                self._delete_expired_user(user)
        logger.info("All expired users have been deleted.")

    def _handle_authenticate_token(self, token, auth_type=None):
        """
        Handler for verifying the authenticate token validity
        """
        try:
            if token == self.__public["token"]:
                return AUTHORIZED_USERS[self.__public["identity"]]
            # Token will always be decoded
            decrypt_identity = jwt.decoding_token(token)["identity"]
            if auth_type is None:
                # Check and remove expired user
                # Currently should only for self.handle_get_authority
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
        if verify_user.get_user_identity() == self.__public["identity"]:
            return False
        del AUTHORIZED_USERS[verify_user.get_user_identity()]
        return True

    def handle_get_one_off_authority(self, one_off_token):
        """
        Handler for returning user access scope if one off token is valid
        """
        verify_user = self._handle_authenticate_token(one_off_token)
        return verify_user.get_user_access_scope()

    async def handle_get_authority(
        self, token: HTTPAuthorizationCredentials = Depends(security)
    ):
        """
        Handler for returning user access scope if token is valid
        """
        verify_user = self._handle_authenticate_token(token.credentials)
        one_off_token = jwt.encoding_token(
            {
                "identity": verify_user.get_user_identity(),
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=60),
            }
        )
        authority = {
            "access_scope": verify_user.get_user_access_scope(),
            "one_off_token": one_off_token,
        }
        return authority

    def _handle_user_authority(self, item, user_yaml):
        """
        Handler for generating user authority object
        """
        email = item.email
        expiration = item.expiration
        identity = f"{email}>{item.machine}>{expiration}"
        if email in user_yaml and expiration != "false":
            # Avoid user object expired but not removed
            # Provide auto renew ability when user request access
            # Always return valid user object
            self._delete_expired_user(identity)
            if identity in AUTHORIZED_USERS:
                return AUTHORIZED_USERS[identity]
            policies = user_yaml[email]["policies"]
            access_scope = self.__es.get("gen3").process_program_project(policies)
            expire_time = datetime.fromtimestamp(int(expiration) / 1000)
            user = User(identity, access_scope, expire_time)
            AUTHORIZED_USERS[identity] = user
            return user
        return AUTHORIZED_USERS[self.__public["identity"]]

    def generate_access_token(self, identity):
        """
        Handler for generating gen3 access_token to limit user access scope
        """
        user_yaml = self.__es.get("irods").process_gen3_user_yaml()
        user = self._handle_user_authority(identity, user_yaml)
        access_token = jwt.encoding_token(
            {
                "identity": user.get_user_identity(),
                "scope": user.get_user_access_scope(),
                "expire": str(user.get_user_expire_time()),
            }
        )
        return access_token

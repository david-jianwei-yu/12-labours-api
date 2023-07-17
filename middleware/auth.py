import json
import yaml

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from yaml import SafeLoader

from app.config import Gen3Config, iRODSConfig
from middleware.jwt import JWT
from middleware.user import User

security = HTTPBearer()
jwt = JWT()


class Authenticator(object):
    def __init__(self):
        self.authorized_user = {
            "public": User("public", [Gen3Config.PUBLIC_ACCESS.split("-")[0]])
        }

    def authenticate_token(self, token):
        try:
            if token == "undefined":
                return self.authorized_user["public"]
            else:
                decrypt_email = jwt.decoding_tokens(token)["email"]
                return self.authorized_user[decrypt_email]
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_user_access_scope(self, token: HTTPAuthorizationCredentials = Depends(security)):
        verify_user = self.authenticate_token(token.credentials)
        result = {
            "policies": verify_user.get_user_policies()
        }
        return result

    async def revoke_user_authority(self, token: HTTPAuthorizationCredentials = Depends(security)):
        verify_user = self.authenticate_token(token.credentials)
        if verify_user.get_user_email() == "public":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Unable to remove default access authority")

        del self.authorized_user[verify_user.get_user_email()]
        return True

    def create_user_authority(self, email, userinfo):
        if email in userinfo:
            if email in self.authorized_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=f"{email} has already been authorized")

            user = User(email, userinfo[email]["policies"])
            self.authorized_user[email] = user
            return user
        else:
            return self.authorized_user["public"]

    def generate_access_token(self, email, SESSION):
        try:
            SESSION.cleanup()
            user_obj = SESSION.data_objects.get(
                f"{iRODSConfig.IRODS_ENDPOINT_URL}/user.yaml")
            yaml_string = ""
            with user_obj.open("r") as f:
                for line in f:
                    yaml_string += str(line, encoding='utf-8')
            yaml_dict = yaml.load(yaml_string, Loader=SafeLoader)
            yaml_json = json.loads(json.dumps(yaml_dict))["users"]

            user = self.create_user_authority(email, yaml_json)
            access_token = jwt.encoding_tokens(user)
            return access_token
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User data not found in the provided path")

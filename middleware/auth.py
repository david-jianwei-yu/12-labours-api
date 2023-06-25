import re
import json
import yaml

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from yaml import SafeLoader
from cryptography.fernet import Fernet

from app.config import iRODSConfig

security = HTTPBearer()


class Authenticator:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        self.access_token = None
        self.authorized_email = None
        self.public_access = False
        self.current_user = None

    def match_user_policies(self, email, userinfo):
        if email in userinfo:
            return userinfo[email]["policies"]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Email {email} is not authorized")

    def generate_access_token(self, email, SESSION):
        obj = SESSION.data_objects.get(
            f"{iRODSConfig.IRODS_ENDPOINT_URL}/user.yaml")
        yaml_string = ""
        with obj.open("r") as f:
            for line in f:
                yaml_string += str(line, encoding='utf-8')
        yaml_dict = yaml.load(yaml_string, Loader=SafeLoader)
        yaml_json = json.loads(json.dumps(yaml_dict))["users"]
        policy_list = self.match_user_policies(email, yaml_json)
        gen3_access = {
            "email": email,
            "policies": policy_list
        }
        self.access_token = self.fernet.encrypt(str(gen3_access).encode())
        self.authorized_email = email
        return self.access_token

    def authenticate_token(self, token):
        try:
            if token == "publicaccesstoken":
                self.public_access = True
                return self.public_access
            else:
                self.current_user = json.loads(
                    re.sub("'", '"', self.fernet.decrypt(token).decode()))
                return self.current_user["email"] == self.authorized_email
        except Exception:
            pass

    async def get_user_authority(self,  token: HTTPAuthorizationCredentials = Depends(security)):
        if not self.authenticate_token(token.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = {
            "policies": ["demo1"],
        }
        if not self.public_access:
            result["policies"] = self.current_user["policies"]
        return result

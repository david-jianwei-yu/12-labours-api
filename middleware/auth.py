import re
import json
import yaml

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from yaml import SafeLoader
from cryptography.fernet import Fernet

from app.config import iRODSConfig

security = HTTPBearer()


class User:
    def __init__(self, email, policies):
        self.user_email = email
        self.user_policies = policies

    def get_user_detail(self):
        user = {
            "email": self.user_email,
            "policies": self.user_policies
        }
        return user


class Authenticator:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        self.authorized_user = {}

    def create_user_authority(self, email, userinfo):
        if email in userinfo:
            if email not in self.authorized_user:
                user = User(email, userinfo[email]["policies"])
                self.authorized_user[email] = user
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=f"Email {email} has already been authorized")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Email {email} is not authorized")

    def revoke_user_authority(self, email):
        try:
            del self.authorized_user[email]
            return True
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Email {email} does not have any extra access")

    def generate_access_token(self, email, SESSION):
        obj = SESSION.data_objects.get(
            f"{iRODSConfig.IRODS_ENDPOINT_URL}/user.yaml")
        yaml_string = ""
        with obj.open("r") as f:
            for line in f:
                yaml_string += str(line, encoding='utf-8')
        yaml_dict = yaml.load(yaml_string, Loader=SafeLoader)
        yaml_json = json.loads(json.dumps(yaml_dict))["users"]

        user = self.create_user_authority(email, yaml_json)
        access_token = self.fernet.encrypt(
            str(user.get_user_detail()).encode())
        return access_token

    def authenticate_token(self, token):
        try:
            if token == "publicaccesstoken":
                return "public_access"
            else:
                decrypt_email = json.loads(
                    re.sub("\'", '\"', self.fernet.decrypt(token).decode()))["email"]
                if decrypt_email not in self.authorized_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                return self.authorized_user[decrypt_email]
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def get_user_access_scope(self,  token: HTTPAuthorizationCredentials = Depends(security)):
        result = {
            "policies": ["demo1"],
        }
        verify_user = self.authenticate_token(token.credentials)
        if verify_user != "public_access":
            result["policies"] = verify_user.get_user_detail()["policies"]
        return result

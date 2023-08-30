import re
import json
import yaml

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from yaml import SafeLoader
from multiprocessing import Manager
from datetime import datetime, timedelta

from app.config import Gen3Config, iRODSConfig
from middleware.jwt import JWT
from middleware.user import User

security = HTTPBearer()
manager = Manager()
jwt = JWT()


class Authenticator(object):
    def __init__(self):
        self.authorized_user = manager.dict()
        self.authorized_user["public"] = User(
            "public",
            [Gen3Config.GEN3_PUBLIC_ACCESS],
            None
        )
        self.expire = 2

    def delete_expired_user(self, user):
        if user in self.authorized_user and user != "public":
            current_time = datetime.utcnow()
            expire_time = self.authorized_user[user].get_user_expire_time()
            if current_time >= expire_time:
                del self.authorized_user[user]

    def cleanup_authorized_user(self):
        for user in list(self.authorized_user):
            if user != "public":
                self.delete_expired_user(user)
        print("All expired users have been deleted.")

    def authenticate_token(self, token, auth_type=None):
        try:
            if token == "undefined":
                return self.authorized_user["public"]
            else:
                # Token will always be decoded
                decrypt_identity = jwt.decoding_tokens(token)["identity"]
                if auth_type == None:
                    # Check and remove expired user
                    # Currently should only for self.gain_user_authority
                    self.delete_expired_user(decrypt_identity)
                return self.authorized_user[decrypt_identity]
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid authentication credentials",
                                headers={"WWW-Authenticate": "Bearer"})

    async def revoke_user_authority(self, token: HTTPAuthorizationCredentials = Depends(security)):
        verify_user = self.authenticate_token(token.credentials, "revoke")
        if verify_user.get_user_identity() == "public":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Unable to remove default access authority")

        del self.authorized_user[verify_user.get_user_identity()]
        return True

    async def gain_user_authority(self, token: HTTPAuthorizationCredentials = Depends(security)):
        verify_user = self.authenticate_token(token.credentials)
        return verify_user.get_user_scope()

    def update_name_list(self, data, path, type_name=None):
        name_list = []
        for ele in data["links"]:
            ele = ele.replace(path, "")
            if type_name == "access":
                ele = re.sub('/', '-', ele)
            name_list.append(ele)
        return name_list

    def generate_access_scope(self, policies, SUBMISSION):
        try:
            program = SUBMISSION.get_programs()
            program_list = self.update_name_list(
                program, "/v0/submission/")
            restrict_program = list(
                set(policies).intersection(program_list))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=str(e))

        project = {"links": []}
        for prog in restrict_program:
            project["links"] += SUBMISSION.get_projects(prog)["links"]
        access_scope = self.update_name_list(
            project, "/v0/submission/", "access")
        return access_scope

    def create_user_authority(self, identity, userinfo, SUBMISSION):
        email = identity.split(">")[0]
        if email in userinfo:
            # Avoid user object expired but not removed
            # Provide auto renew ability when user request access
            # Always return valid user object
            self.delete_expired_user(identity)
            if identity in self.authorized_user:
                return self.authorized_user[identity]
            else:
                policies = userinfo[email]["policies"]
                scope = self.generate_access_scope(policies, SUBMISSION)
                expire_time = datetime.utcnow() + timedelta(hours=self.expire)
                user = User(identity, scope, expire_time)
                self.authorized_user[identity] = user
                return user
        else:
            return self.authorized_user["public"]

    def generate_access_token(self, identity, SUBMISSION, SESSION):
        try:
            yaml_string = ""
            user_obj = SESSION.data_objects.get(
                f"{iRODSConfig.IRODS_ROOT_PATH}/user.yaml")
            with user_obj.open("r") as f:
                for line in f:
                    yaml_string += str(line, encoding='utf-8')
            yaml_dict = yaml.load(yaml_string, Loader=SafeLoader)
            yaml_json = json.loads(json.dumps(yaml_dict))["users"]
        except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User data not found in the provided path")

        user = self.create_user_authority(identity, yaml_json, SUBMISSION)
        payload = {
            "nbf": datetime.utcnow(),
            "identity": user.get_user_identity(),
            "scope": user.get_user_scope(),
        }
        access_token = jwt.encoding_tokens(payload)
        return access_token

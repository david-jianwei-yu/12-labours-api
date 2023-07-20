from datetime import datetime, timedelta

class User(object):
    def __init__(self, identity, policies):
        self.identity = identity
        self.policies = policies
        self.expire_time = datetime.utcnow() + timedelta(hours=2)

    def get_user_identity(self):
        return self.identity

    def get_user_policies(self):
        return self.policies
    
    def get_user_expire_time(self):
        return self.expire_time

    def get_user_detail(self):
        user = {
            "identity": self.identity,
            "policies": self.policies,
            "expire_time": self.expire_time
        }
        return user

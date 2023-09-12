class User:
    def __init__(self, identity, scope, expire_time):
        self.identity = identity
        self.scope = scope
        self.expire_time = expire_time

    def get_user_identity(self):
        return self.identity

    def get_user_scope(self):
        return self.scope

    def get_user_expire_time(self):
        return self.expire_time

    def get_user_detail(self):
        user = {
            "identity": self.identity,
            "scope": self.scope,
            "expire_time": self.expire_time,
        }
        return user

class User(object):
    def __init__(self, identity, policies):
        self.identity = identity
        self.policies = policies

    def get_user_identity(self):
        return self.identity

    def get_user_policies(self):
        return self.policies

    def get_user_detail(self):
        user = {
            "identity": self.identity,
            "policies": self.policies
        }
        return user

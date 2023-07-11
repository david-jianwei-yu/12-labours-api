class User(object):
    def __init__(self, email, policies):
        self.email = email
        self.policies = policies

    def get_user_email(self):
        return self.email

    def get_user_policies(self):
        return self.policies

    def get_user_detail(self):
        user = {
            "email": self.email,
            "policies": self.policies
        }
        return user

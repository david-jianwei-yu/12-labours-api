import jwt

from datetime import datetime, timedelta

from app.config import Config


class JWT(object):
    def __init__(self):
        self.algorithm = "HS256"
        self.secure = Config.JWT_SECURE_KEY

    def encoding_tokens(self, user):
        payload = {
            "nbf": datetime.utcnow(),
            "identity": user.get_user_identity(),
            "policies": user.get_user_policies(),
        }
        encoded = jwt.encode(payload, self.secure, self.algorithm)
        return encoded

    def decoding_tokens(self, token):
        decoded = jwt.decode(token, self.secure, self.algorithm)
        return decoded

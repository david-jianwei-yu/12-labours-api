import jwt

from datetime import datetime, timedelta

from app.config import Config


class JWT(object):
    def __init__(self):
        self.expire_time = 12
        self.algorithm = "HS256"
        self.secure = Config.JWT_SECURE_KEY

    def encoding_tokens(self, user):
        payload = {
            "exp": datetime.utcnow() + timedelta(hours=self.expire_time),
            "nbf": datetime.utcnow(),
            "email": user.get_user_email(),
            "policies": user.get_user_policies(),
        }
        encoded = jwt.encode(payload, self.secure, self.algorithm)
        return encoded

    def decoding_tokens(self, token):
        decoded = jwt.decode(token, self.secure, self.algorithm)
        return decoded

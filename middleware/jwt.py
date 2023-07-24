import jwt

from app.config import Config


class JWT(object):
    def __init__(self):
        self.algorithm = "HS256"
        self.secure = Config.JWT_SECURE_KEY

    def encoding_tokens(self, payload):
        encoded = jwt.encode(payload, self.secure, self.algorithm)
        return encoded

    def decoding_tokens(self, token):
        decoded = jwt.decode(token, self.secure, self.algorithm)
        return decoded

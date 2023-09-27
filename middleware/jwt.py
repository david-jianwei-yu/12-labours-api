"""
Functionality for encoding/decoding access token
- encoding_token
- decoding_token
"""
import jwt

from app.config import Config


class JWT:
    """
    Security functionality
    """

    def __init__(self):
        self.algorithm = "HS256"
        self.secure = Config.JWT_SECURE_KEY

    def encoding_token(self, payload):
        """
        Handler for encoding token
        """
        encoded = jwt.encode(payload, self.secure, self.algorithm)
        return encoded

    def decoding_token(self, token):
        """
        Handler for decoding token
        """
        decoded = jwt.decode(token, self.secure, self.algorithm)
        return decoded

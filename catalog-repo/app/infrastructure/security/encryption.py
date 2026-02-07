"""Encryption utilities for sensitive data."""

from cryptography.fernet import Fernet
from app.config.settings import get_settings


class Encryptor:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self):
        settings = get_settings()
        # In production, load from secure key management service
        self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


encryptor = Encryptor()

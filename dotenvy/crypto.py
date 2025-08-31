import os
from cryptography.fernet import Fernet

CONFIG_DIR = os.path.expanduser("~/.dotenvy")
KEY_FILE = os.path.join(CONFIG_DIR, "key")

class CryptoManager:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _get_or_create_key(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)
        
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, "wb") as key_file:
                key_file.write(key)
            return key
    
    def encrypt(self, content: str) -> bytes:
        return self.fernet.encrypt(content.encode())
    
    def decrypt(self, file_path) -> str:
        with open(file_path, "rb") as f: 
            token = f.read()
        return self.fernet.decrypt(token).decode()
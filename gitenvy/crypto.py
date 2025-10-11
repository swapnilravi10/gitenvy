from pathlib import Path
from cryptography.fernet import Fernet


class CryptoManager:
    def __init__(self, key_path: Path):
        self.key_path = key_path
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        # Ensure directory exists
        self.key_path.parent.mkdir(parents=True, exist_ok=True)

        if self.key_path.exists():
            return self.key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)
            return key
    
    def encrypt(self, content: str) -> bytes:
        return self.fernet.encrypt(content.encode())
    
    def decrypt(self, file_path:Path | str) -> str:
        file_path = Path(file_path)
        token = file_path.read_bytes()
        return self.fernet.decrypt(token).decode()
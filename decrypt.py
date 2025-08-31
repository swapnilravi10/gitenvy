from cryptography.fernet import Fernet
from pathlib import Path

KEY_FILE = Path.home() / ".dotenvy" / "key"
ENCRYPTED_FILE = Path(".env.enc")
DECRYPTED_FILE = Path(".env")

with open(KEY_FILE, "rb") as keyfile:
    key = keyfile.read()

cipher = Fernet(key)

with open(ENCRYPTED_FILE, "rb") as encfile:
    encrypted_data = encfile.read()

decrypted_data = cipher.decrypt(encrypted_data)

with open(DECRYPTED_FILE, "wb") as decfile:
    decfile.write(decrypted_data)

print(f"✅ {ENCRYPTED_FILE} decrypted → {DECRYPTED_FILE}")
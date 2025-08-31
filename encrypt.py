import os
from cryptography.fernet import Fernet

# 🔑 Step 1: Generate/load key
key_file = os.path.expanduser("~/.dotenvy/key")
if not os.path.exists(key_file):
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)
    print(f"New key generated at {key_file}")
else:
    with open(key_file, "rb") as f:
        key = f.read()

cipher = Fernet(key)

# 🔐 Step 2: Encrypt .env
with open(".env", "rb") as f:
    plaintext = f.read()

encrypted = cipher.encrypt(plaintext)

with open(".env.enc", "wb") as f:
    f.write(encrypted)

print("✅ .env encrypted → .env.enc")

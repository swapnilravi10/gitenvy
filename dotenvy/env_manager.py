# dotenvy/env_manager.py
import os
from git import Repo, GitCommandError
from .crypto import CryptoManager
from .config_manager import ConfigManager
import getpass
from datetime import datetime
import json

class EnvManager:
    def __init__(self, project: str, env_name: str, repo_path: str = None):
        """
        repo_path: path to your local clone of the private repo
        """
        self.project = project
        self.env_name = env_name
        self.crypto = CryptoManager()

        cm = ConfigManager()
        cfg = cm.load()

        self.repo_path = cfg.get("repo_path")
        if not self.repo_path:
            raise RuntimeError("dotenvy not initialized. Run `dotenvy init --repo <URL>` first.")

        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize git repo at {self.repo_path}: {e}")

    def push(self, env_file: str = ".env"):
        """Encrypt and push the .env file to the git repo"""

        if not os.path.exists(env_file):
            raise FileNotFoundError("No .env file found in current directory")

        # encrypt
        with open(env_file, "r") as f:
            content = f.read()
        encrypted = self.crypto.encrypt(content)

        # version folder
        base_dir = os.path.join(self.repo_path, self.project, self.env_name)
        os.makedirs(base_dir, exist_ok=True)

        existing_versions = [int(name) for name in os.listdir(base_dir) if name.isdigit()]
        next_version = str(max(existing_versions, default=0) + 1)

        out_dir = os.path.join(base_dir, next_version)
        os.makedirs(out_dir, exist_ok=True)

        # write metadata
        metadata = {
            "last_updated_by": getpass.getuser(),
            "last_updated_at": datetime.utcnow().isoformat() + "Z",
            "version": int(next_version)
        }

        with open(os.path.join(out_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        # write encrypted file
        out_file = os.path.join(out_dir, ".env.enc")
        with open(out_file, "wb") as f:
            f.write(encrypted)

        # commit & push to git
        try:
            self.repo.git.add(all=True)
            self.repo.index.commit(f"Add {self.project}/{self.env_name} version {next_version}")
            origin = self.repo.remote(name="origin")
            origin.push()
        except GitCommandError as e:
            print(f"⚠️ Git error: {e}")

        return out_file
    
    def pull(self, version: str = "latest", out_path: str = ".env"):
        """
        Pull a version of .env from git, decrypt, and save locally
        version: "latest" or specific version number
        out_path: where to save decrypted .env
        """
        import os

        base_dir = os.path.join(self.repo_path, self.project, self.env_name)
        if not os.path.exists(base_dir):
            raise FileNotFoundError(f"No versions found for {self.project}/{self.env_name}")

        # find latest version
        versions = sorted([v for v in os.listdir(base_dir) if v.isdigit()], key=int)
        if not versions:
            raise FileNotFoundError("No versions found")

        if version == "latest":
            version = versions[-1]
        elif version not in versions:
            raise ValueError(f"Version {version} not found")

        enc_file = os.path.join(base_dir, version, ".env.enc")
        if not os.path.exists(enc_file):
            raise FileNotFoundError(f"Encrypted file missing for version {version}")

        # decrypt
        decrypted_data = self.crypto.decrypt(enc_file)

        # save locally
        with open(out_path, "w") as f:
            f.write(decrypted_data)

        return out_path
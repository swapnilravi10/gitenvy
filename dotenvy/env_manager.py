from pathlib import Path
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

        self.repo_path = Path(repo_path) if repo_path else Path(cfg.get("repo_path", ""))
        if not self.repo_path.exists():
            raise RuntimeError("dotenvy not initialized. Run `dotenvy init --repo <URL>` first.")

        try:
            self.repo = Repo(self.repo_path)
        except GitCommandError as e:
            raise RuntimeError(f"Failed to initialize git repo at {self.repo_path}: {e}")
        self.git_user_name = getpass.getuser()  # fallback
        try:
            self.git_user_name = self.repo.config_reader().get_value("user", "name")
        except (KeyError, IOError):
            # fallback to system username if git config not set
            pass

    def push(self, env_file: str = ".env"):
        """Encrypt and push the .env file to the git repo"""

        env_file_path = Path(env_file)
        if not env_file_path.exists():
            raise FileNotFoundError("No .env file found in current directory")

        encrypted = self.crypto.encrypt(env_file_path.read_text())

        base_dir = Path(self.repo_path) / self.project / self.env_name
        base_dir.mkdir(parents=True, exist_ok=True)

        existing_versions = [int(p.name) for p in base_dir.iterdir() if p.name.isdigit()]
        next_version = str(max(existing_versions, default=0) + 1)

        out_dir = base_dir / next_version
        out_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "last_updated_by": self.git_user_name,
            "last_updated_at": datetime.utcnow().isoformat() + "Z",
            "version": int(next_version)
        }
        (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

        out_file = out_dir / ".env.enc"
        out_file.write_bytes(encrypted)

        # commit & push to git
        try:
            self.repo.git.add(all=True)
            self.repo.index.commit(f"Add {self.project}/{self.env_name} version {next_version}")
            self.repo.remote(name="origin").push()
        except GitCommandError as e:
            print(f"⚠️ Git error: {e}")

        return out_file
    
    def pull(self, version: str = "latest", out_path: str = ".env"):
        """Pull a version of .env from git, decrypt, and save locally"""
        base_dir = self.repo_path / self.project / self.env_name
        if not base_dir.exists():
            raise FileNotFoundError(f"No versions found for {self.project}/{self.env_name}")

        versions = sorted([v.name for v in base_dir.iterdir() if v.name.isdigit()], key=int)
        if not versions:
            raise FileNotFoundError("No versions found")
        if version == "latest":
            version = versions[-1]
        elif version not in versions:
            raise ValueError(f"Version {version} not found")
        
        enc_file = base_dir / version / ".env.enc"
        if not enc_file.exists():
            raise FileNotFoundError(f"Encrypted file missing for version {version}")

        decrypted_data = self.crypto.decrypt(enc_file)
        out_file = Path(out_path)
        out_file.write_text(decrypted_data)

        return out_file
# dotenvy/env_manager.py
import os
from git import Repo, GitCommandError
from .crypto import CryptoManager

class EnvManager:
    def __init__(self, project: str, env_name: str, repo_path: str = "dotenvy-store"):
        """
        repo_path: path to your local clone of the private repo
        """
        self.project = project
        self.env_name = env_name
        self.crypto = CryptoManager()
        self.repo_path = repo_path

        # open the repo
        if not os.path.exists(repo_path):
            raise FileNotFoundError(f"Git repo path '{repo_path}' does not exist")
        self.repo = Repo(repo_path)

    def push(self, env_file: str = ".env"):
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

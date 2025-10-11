from pathlib import Path
from git import Repo, GitCommandError
from .crypto import CryptoManager
from .config_manager import ConfigManager
import getpass
from datetime import datetime
import json
import os
import subprocess

class EnvManager:
    def __init__(self, project: str, env_name: str, repo_name:str):
        """
        repo_path: path to your local clone of the private repo
        """
        if not project or not env_name:
            raise ValueError("Project and environment name must not be empty.")

        self.project = project
        self.env_name = env_name

        cm = ConfigManager()
        cfg = cm.load()

        repo_key_path = cfg.get("configs", {}).get(repo_name, {}).get("key_path")
        self.repo_key_path = Path(os.path.expanduser(repo_key_path))
        self.crypto = CryptoManager(self.repo_key_path)

        repo_path = cfg.get("configs", {}).get(repo_name, {}).get("repo_path")
        self.repo_path = Path(os.path.expanduser(repo_path))
        if not self.repo_path.exists():
            raise FileNotFoundError( f"Repo path does not exist: {self.repo_path}. "
        "Run `gitenvy init --repo <URL>` first or check your config.")

        try:
            self.repo = Repo(str(self.repo_path))
        except GitCommandError as e:
            raise RuntimeError(f"Git error: {e}")

        try:
            self.git_user_name = self.repo.config_reader().get_value("user", "name")
        except (KeyError, IOError, AttributeError):
            self.git_user_name = getpass.getuser()  # fallback

    @staticmethod
    def init_repo(repo_url, path, branch=None):
        """
        Clone the repo if not exists, or pull and switch branch if exists.
        Returns: dict with 'success' (bool) and 'message' (str)
        """
        git_dir = os.path.join(path, ".git")
        if not os.path.exists(path):
            clone_cmd = ["git", "clone"]
            if branch:
                clone_cmd += ["-b", branch]
            clone_cmd += [repo_url, path]
            try:
                subprocess.run(clone_cmd, check=True)
                return {
                    "success": True,
                    "message": f"✅ Repo cloned successfully{' on branch ' + branch if branch else ''}"
                }
            except subprocess.CalledProcessError as e:
                return {
                    "success": False,
                    "message": f"⚠️ Git clone failed: {e}"
                }
        else:
            if os.path.exists(git_dir):
                try:
                    repo_obj = Repo(path)
                    repo_obj.remotes.origin.fetch()
                    if branch:
                        if branch in [b.name for b in repo_obj.branches]:
                            repo_obj.git.checkout(branch)
                        else:
                            repo_obj.git.checkout("-b", branch, f"origin/{branch}")
                    repo_obj.git.pull()
                    return {
                        "success": True,
                        "message": f"✅ Repo updated{' on branch ' + branch if branch else ''}"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"⚠️ Git operation failed: {e}"
                    }
            else:
                return {
                    "success": False,
                    "message": "⚠️ Path exists but is not a git repo."
                }

    def push(self, env_file: str = ".env"):
        """Encrypt and push the .env file to the git repo"""

        env_file_path = Path(env_file)
        if not env_file_path.exists():
            raise FileNotFoundError(f".env file not found: {env_file_path}")

        try:
            encrypted = self.crypto.encrypt(env_file_path.read_text())
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {e}")

        base_dir = self.repo_path / self.project / self.env_name
        base_dir.mkdir(parents=True, exist_ok=True)

        # Only consider digit-named directories
        existing_versions = [int(p.name) for p in base_dir.iterdir() if p.is_dir() and p.name.isdigit()]
        next_version = str(max(existing_versions, default=0) + 1)

        out_dir = base_dir / next_version
        try:
            out_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            # Handle race condition by bumping version
            next_version = str(max(existing_versions + [int(next_version)], default=0) + 1)
            out_dir = base_dir / next_version
            out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / ".env.enc"
        try:
            out_file.write_bytes(encrypted)
        except PermissionError:
            raise PermissionError(f"No write permission for {out_file}")

        metadata = {
            "last_updated_by": self.git_user_name,
            "last_updated_at": datetime.utcnow().isoformat() + "Z",
            "version": int(next_version)
        }
        (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

        # commit & push to git
        try:
            self.repo.git.add(A=True)
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

        # Only consider digit-named directories
        versions = [int(p.name) for p in base_dir.iterdir() if p.is_dir() and p.name.isdigit()]
        if not versions:
            raise FileNotFoundError("No versions found")

        if version == "latest":
            version = str(max(versions))
        elif version not in map(str, versions):
            raise ValueError(f"Version {version} not found")

        enc_file = base_dir / version / ".env.enc"
        if not enc_file.exists():
            raise FileNotFoundError(f"Encrypted file missing for version {version}")

        try:
            decrypted = self.crypto.decrypt(enc_file)
        except Exception as e:
            raise RuntimeError(f"Decryption failed for version {version}: {e}")

        out_file = Path(out_path)
        try:
            out_file.write_text(decrypted)
        except PermissionError:
            raise PermissionError(f"No write permission for {out_file}")

        return out_file

    
    def list_projects(self):
        """List all projects in the repo (excluding .git)"""
        if not self.repo_path.exists():
            return []
        return [p.name for p in self.repo_path.iterdir() if p.is_dir() and p.name != ".git"]

    def list_envs(self, project: str):
        """List all environments for a given project"""
        project_dir = self.repo_path / project
        if not project_dir.exists():
            return []
        return [p.name for p in project_dir.iterdir() if p.is_dir()]

    def list_versions(self, version: str = None):
        """List all versions (with metadata) or details of a specific version"""
        base_dir = self.repo_path / self.project / self.env_name
        if not base_dir.exists():
            return []

        versions = sorted(
            [p for p in base_dir.iterdir() if p.is_dir() and p.name.isdigit()],
            key=lambda p: int(p.name)
        )

        if not versions:
            return []

        # Handle "latest" alias or explicit version
        if version:
            if version.lower() == "latest":
                version = versions[-1].name
            elif version not in [p.name for p in versions]:
                return []
            versions = [base_dir / version]

        results = []
        for v in versions:
            meta_file = v / "metadata.json"
            if meta_file.exists():
                with meta_file.open() as f:
                    meta = json.load(f)
                results.append({
                    "version": v.name,
                    "last_updated_by": meta.get("last_updated_by", "unknown"),
                    "last_updated_at": meta.get("last_updated_at", "unknown"),
                })
            else:
                results.append({
                    "version": v.name,
                    "last_updated_by": None,
                    "last_updated_at": None,
                })

        return results

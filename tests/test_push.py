import json
from pathlib import Path
import pytest

from dotenvy.env_manager import EnvManager


class DummyCrypto:
    """Fake crypto manager for testing"""
    def encrypt(self, text):
        return b"encrypted:" + text.encode()

    def decrypt(self, path):
        return "decrypted"


class DummyRepo:
    """Fake git.Repo for testing"""
    def __init__(self, path):
        self.git = self
        self.index = self
        self._commits = []
        self._pushed = False

    def add(self, all=False):
        return True

    def commit(self, msg):
        self._commits.append(msg)
        return True

    def remote(self, name="origin"):
        return self

    def push(self):
        self._pushed = True
        return True

    def config_reader(self):
        class DummyConfig:
            def get_value(self, section, key):
                return "Test User"
        return DummyConfig()


@pytest.fixture
def temp_repo(tmp_path, monkeypatch):
    # Create fake .env file
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET=123")

    # Patch CryptoManager and Repo
    monkeypatch.setattr("dotenvy.env_manager.CryptoManager", lambda: DummyCrypto())
    monkeypatch.setattr("dotenvy.env_manager.Repo", lambda path: DummyRepo(path))

    # Patch ConfigManager.load to avoid needing a config file
    monkeypatch.setattr("dotenvy.env_manager.ConfigManager", lambda: type("CM", (), {"load": lambda self: {"repo_path": str(tmp_path)}})())

    return tmp_path


def test_push_creates_new_version(temp_repo):
    manager = EnvManager(project="myproj", env_name="dev", repo_path=temp_repo)

    out_file = manager.push(env_file=str(temp_repo / ".env"))

    # ✅ Assert encrypted file exists
    assert out_file.exists()
    assert out_file.read_bytes().startswith(b"encrypted:")

    # ✅ Assert metadata file exists
    metadata_file = out_file.parent / "metadata.json"
    assert metadata_file.exists()
    metadata = json.loads(metadata_file.read_text())
    assert metadata["last_updated_by"] == "Test User"
    assert metadata["version"] == 1

import pytest
from pathlib import Path
import json
from dotenvy.env_manager import EnvManager


@pytest.fixture
def mock_repo(tmp_path, monkeypatch):
    """Create a fake repo structure with an encrypted env file and metadata."""

    project = "myproj"
    env = "dev"
    repo_path = tmp_path / "repo"
    base_dir = repo_path / project / env / "1"
    base_dir.mkdir(parents=True)

    class DummyCrypto:
        def encrypt(self, content): return content.encode()
        def decrypt(self, file_path): return "SECRET=123"

    monkeypatch.setattr("dotenvy.env_manager.CryptoManager", lambda: DummyCrypto())

    enc_file = base_dir / ".env.enc"
    enc_file.write_bytes(b"encrypted-data")

    metadata = {"last_updated_by": "tester", "last_updated_at": "now", "version": 1}
    (base_dir / "metadata.json").write_text(json.dumps(metadata))

    class DummyRepo:
        def __init__(self, path): self.path = path
        def config_reader(self): return self
        def get_value(self, *_args, **_kwargs): return "Test User"

    monkeypatch.setattr("dotenvy.env_manager.Repo", DummyRepo)

    return project, env, repo_path


def test_pull_latest(mock_repo, tmp_path):
    project, env, repo_path = mock_repo
    manager = EnvManager(project, env, repo_path=str(repo_path))

    out_file = tmp_path / ".env"
    result = manager.pull(version="latest", out_path=out_file)

    assert result.exists()
    assert result.read_text() == "SECRET=123"

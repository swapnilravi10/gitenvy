import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from gitenvy.utils.config_builder import ConfigBuilder

class ConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_file = config_path or Path.home() / ".gitenvy" / "config.yml"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}
        self.config_builder = ConfigBuilder()

    def load(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            self._config = {}
            return self._config
        try:
            with open(self.config_file, "r") as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse config file: {self.config_file}") from e
        return self._config
    
    def save(self, config: Dict[str, Any]):
        config = self.config_builder.create_update_yaml_config(
            repo_url=config.get("repo_url", ""),
            repo_path=config.get("repo_path", ""),
            config_name=config.get("config_name", ""),
            branch=config.get("branch", None)
        )
        with open(self.config_file, "w") as f:
            yaml.dump(config, f)
        self._config = config
    
    def set_default(self, repo_name: str):
        if not self._config:
            self.load()
        self._config["default"] = repo_name
        with open(self.config_file, "w") as f:
            yaml.dump(self._config, f)

    def get(self, key, default: Any = None) -> Any:
        if not self._config:
            self.load()
        return self._config.get(key, default)
    
    def get_fernet_key(self, repo_name: str) -> Optional[str]:
        if not self._config:
            self.load()
        repo_cfg = self._config.get("configs", {}).get(repo_name)
        if not repo_cfg:
            raise ValueError(f"Repo name '{repo_name}' not found in config.")
        key_path = Path(repo_cfg.get("key_path", "")).expanduser()
        if not key_path.exists():
            raise FileNotFoundError(f"Key file '{key_path}' does not exist.")
        try:
            with open(key_path, "r") as f:
                key = f.read().strip()
                return key
        except Exception:
            return None
        
    def set_fernet_key(self, repo_name: str, key: str):
        if not self._config:
            self.load()
        repo_cfg = self._config.get("configs", {}).get(repo_name)
        if not repo_cfg:
            raise ValueError(f"Repo name '{repo_name}' not found in config.")
        key_path = Path(repo_cfg.get("key_path", "")).expanduser()
        key_path.parent.mkdir(parents=True, exist_ok=True)
        with open(key_path, "w") as f:
            f.write(key.strip())
        key_path.chmod(0o600)
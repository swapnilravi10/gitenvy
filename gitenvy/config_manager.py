import yaml
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_file = config_path or Path.home() / ".gitenvy" / "config.yml"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config: Dict[str, Any] = {}

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
        with open(self.config_file, "w") as f:
            yaml.dump(config, f)
        self._config = config

    def get(self, key, default: Any = None) -> Any:
        if not self._config:
            self.load()
        return self._config.get(key, default)

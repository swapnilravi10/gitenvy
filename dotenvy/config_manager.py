import os
import yaml
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_file = Path.home() / ".dotenvy" / "config.yml"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config = None

    def load(self):
        if not self.config_file.exists():
            return {}
        with open(self.config_file, "r") as f:
            self._config = yaml.safe_load(f) or {}
        return self._config

    def save(self, config):
        with open(self.config_file, "w") as f:
            yaml.dump(config, f)
        self._config = config

    def get(self, key, default=None):
        if self._config is None:
            self.load()
        return self._config.get(key, default)

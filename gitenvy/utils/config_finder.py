import os
import yaml
from typing import Any, Dict

class ConfigFinder:
    
    def __init__(self, config_file="~/.gitenvy/config.yml"):
        self.config_file = os.path.expanduser(config_file)

    def get_default_repo_path(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                default_config = yaml.safe_load(f) or {}
                default_repo = default_config.get("default", {})
                return default_config.get("configs", {}).get(default_repo, {}).get("repo_path", "")
        return {}

    def get_default_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                default_config = yaml.safe_load(f) or {}
                return default_config.get("default", {})
        return {}

    def get_default_key_path(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                default_config = yaml.safe_load(f) or {}
                default_repo = default_config.get("default", {})
                return default_config.get("configs", {}).get(default_repo, {}).get("key_path", "")
        return {}
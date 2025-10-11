import os
import yaml
from urllib.parse import urlparse
import pathlib

class ConfigBuilder:
    def __init__(self, config_file="~/.gitenvy/config.yml"):
        self.config_file = os.path.expanduser(config_file)
    
    def create_update_yaml_config(self, repo_url: str, repo_path: str, config_name: str, branch: str = None):
        new_config = {
            "repo_url": f"{repo_url}",
            "repo_path": f"{repo_path}",
            "key_path": f"~/.gitenvy/keys/{config_name}.key",
            "branch": branch
        }
        # Load existing config if file exists
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}

        # Ensure 'configs' key exists
        if "configs" not in config_data:
            config_data["configs"] = {}
            # Set default only when adding for the first time
            config_data["default"] = config_name

        # Add or update config
        config_data["configs"][config_name] = new_config

        return config_data
    
    def extract_repo_name(self, repo_url: str) -> str:
        if repo_url.startswith("http"):
            path = urlparse(repo_url).path
            return pathlib.Path(path).stem  # removes .git automatically
        else:  # SSH format
            return pathlib.Path(repo_url.split(":")[-1]).stem
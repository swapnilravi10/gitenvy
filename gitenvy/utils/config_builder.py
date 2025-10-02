import os
import yaml

class ConfigBuilder:
    def __init__(self, config_file="~/.gitenvy/config.yml"):
        self.config_file = os.path.expanduser(config_file)
    
    def create_update_yaml_config(self, repo_url: str, repo_path: str, config_name: str):
        new_config =  {
                    "repo_url": f"{repo_url}",
                    "repo_path": f"{repo_path}",
                    "key_path": f"~/.gitenvy/keys/{config_name}.key"
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

        # Write back to file
        with open(self.config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

        return config_data
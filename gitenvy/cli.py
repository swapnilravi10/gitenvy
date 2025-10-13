import click
from gitenvy.env_manager import EnvManager
from gitenvy.config_manager import ConfigManager
from gitenvy.utils.config_builder import ConfigBuilder
import os
from pathlib import Path
from gitenvy.utils.helper import *

DEFAULT_REPO_PATH = os.path.expanduser("~/.gitenvy/repos")

@click.group()
def cli():
    """gitenvy - manage environment variables securely."""
    pass

@cli.command()
@click.argument("repo")
@click.option("--path", default=DEFAULT_REPO_PATH, help="Local path to clone the repo")
@click.option("--branch", default=None, help="Branch to clone or checkout after cloning")
def init(repo, path, branch):
    """
    Initialize gitenvy by cloning the env repo and saving config. \n

    Usage: \n
        - gitenvy init <repo_url> \n
        Initialize git repo.

        - gitenvy init <repo_url> --path <local_path> \n
        Initialize git repo at specified local path.

        - gitenvy init <repo_url> --branch <branch_name> \n
        Initialize git repo and checkout specified branch.
    """

    config_builder = ConfigBuilder()
    config_name = config_builder.extract_repo_name(repo)
    path = os.path.expanduser(os.path.join(path, config_name))

    result = EnvManager.init_repo(repo, path, branch)
    click.echo(result["message"])

    if result["success"]:
        cm = ConfigManager()
        cm.save({
            "repo_url": repo,
            "repo_path": path,
            "config_name": config_name,
            "branch": branch
        })
        click.echo(f"Config saved: {repo} -> {path}")
    else:
        click.echo("Config not saved due to repo error.")


@cli.command()
@click.option('--project', required=True, help='Project name')
@click.option('--env','--env-name', required=True, help='Environment name (e.g., dev, prod)')
@click.option("--repo-name", required=False, help="Name of the repo as in config")
def push(project, env, repo_name):
    """
    Push .env file for a specific project and environment. \n
    
    Usage: \n
        - gitenvy push --project <PROJECT> --env <ENV> \n
        Encrypts and pushes the .env file to the specified project and environment. Uses default repo.

        - gitenvy push --project <PROJECT> --env <ENV> --repo-name <REPO_NAME> \n
        Same as above, but specifies which repo config to use if multiple are configured.
    """
    cm = ConfigManager()
    config = cm.load()
    
    if repo_name:
        repo_cfg = config['configs'].get(repo_name)
        if not repo_cfg:
            click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
            return
    else:
        default_name = config.get('default')
    manager = EnvManager(project, env, repo_name=repo_name or default_name)
    try:
        out_file = manager.push()
        click.echo(f"Encrypted .env file stored at: {out_file}")
    except FileNotFoundError as e:
        click.echo(str(e))
    except PermissionError as e:
        click.echo(f"🚫 Permission error: {e}")
    except RuntimeError as e:
        click.echo(f"❌ Git/Sync/Decryption error: {e}")
    except Exception as e:
        click.echo(f"💥 Unexpected error: {type(e).__name__}: {e}")

@cli.command(name="list")
@click.option("--repo-name", required=False, help="Name of the repo as in config")
@click.option("--project", required=False, help="Project name")
@click.option("--env", "--env-name", required=False, help="Environment name")
def list_config(repo_name, project, env):
    """
    List all repo names in your config, marking the default.

    Usage: \n
        - gitenvy list \n
        Lists all configured repos. Marks the default repo.

        - gitenvy list --repo-name <REPO_NAME> \n
        Lists all projects in the specified repo.

        - gitenvy list --repo-name <REPO_NAME> --project <PROJECT> \n
        Lists all environments in the specified project of the specified repo.

        - gitenvy list --repo-name <REPO_NAME> --project <PROJECT> --env <ENV> \n
        Lists all versions in the specified environment of the specified project and repo. 
        Shows last updated by and timestamp.
    """
    cm = ConfigManager()
    config = cm.load()

    if repo_name and project and env:
        repo_cfg = config['configs'].get(repo_name)
        if not repo_cfg:
            click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
            return
        repo_path = repo_cfg['repo_path']
        get_version_table(repo_path, repo_name, project, env)
    elif repo_name and project:
        repo_cfg = config['configs'].get(repo_name)
        if not repo_cfg:
            click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
            return
        repo_path = repo_cfg['repo_path']
        get_env_table(repo_path, repo_name, project)
    elif repo_name:
        repo_cfg = config['configs'].get(repo_name)
        if not repo_cfg:
            click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
            return
        repo_path = repo_cfg['repo_path']
        get_project_table(repo_path, repo_name)
    else:
        get_repo_table(config)
    

@cli.command()
@click.option("--project", required=True)
@click.option("--env", "--env-name", required=True)
@click.option("--version", default="latest", help="Version to pull")
@click.option("--out-path", default=".env", help="Where to save decrypted .env on machine")
@click.option("--repo-name", required=False, help="Name of the repo as in config")
def pull(project, env, version, out_path, repo_name):
    """
    Pull .env for a specific project and environment. \n

    Usage: \n
        - gitenvy pull --project <PROJECT> --env <ENV> \n
        Decrypts and saves the latest version of the .env file for the specified project and environment. Uses default repo.

        - gitenvy pull --project <PROJECT> --env <ENV> --version <VERSION> \n
        Same as above, but pulls the specified version instead of the latest.

        - gitenvy pull --project <PROJECT> --env <ENV> --out-path <PATH> \n
        Same as above, but saves the decrypted .env file to the specified path. 
        Out-path can be absolute or relative. Defaults to './.env'. 

        - gitenvy pull --project <PROJECT> --env <ENV> --repo-name <REPO_NAME> \n
        Same as above, but specifies which repo config to use if multiple are configured.
    """
    cm = ConfigManager()
    config = cm.load()
    if repo_name:
        repo_cfg = config['configs'].get(repo_name)
        if not repo_cfg:
            click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
            return
    else:
        default_name = config.get('default')
    manager = EnvManager(project, env, repo_name=repo_name or default_name)
    try:
        file_path = manager.pull(version=version, out_path=out_path)
        click.echo(f"✅ Decrypted .env saved to {file_path}")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"⚠️ {str(e)}")
    except PermissionError as e:
        click.echo(f"🚫 Permission error: {e}")
    except RuntimeError as e:
        click.echo(f"❌ Git/Sync/Decryption error: {e}")
    except Exception as e:
        click.echo(f"💥 Unexpected error: {type(e).__name__}: {e}")

@cli.command(name="set-default")
@click.argument("repo_name")
def set_default(repo_name):
    """
    Set the default repo to use when none is specified. \n

    Usage: \n
        - gitenvy set-default <REPO_NAME> \n
        Sets the specified repo as the default in your config.
    """
    cm = ConfigManager()
    config = cm.load()
    if repo_name not in config.get("configs", {}):
        click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
        return
    try:
        cm.set_default(repo_name)
        click.echo(f"✅ Default repo set to '{repo_name}'")
    except Exception as e:
        click.echo(f"⚠️ Failed to set default: {e}")
    except PermissionError as e:
        click.echo(f"🚫 Permission error: {e}")
    except RuntimeError as e:
        click.echo(f"❌ Git/Sync/Decryption error: {e}")

@cli.command(name="get-key")
@click.argument("repo_name")
def get_key(repo_name):
    """
    Get the Fernet key for a specific repo. \n
    Usage: \n
        - gitenvy get-key <REPO_NAME> \n
        Retrieves and displays the Fernet key for the specified repo.
    """
    cm = ConfigManager()
    config = cm.load()
    repo_cfg = config['configs'].get(repo_name)
    if not repo_cfg:
        click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
        return
    try:
        key = cm.get_fernet_key(repo_name)
        if key:
            click.echo(f"'{repo_name}': {key}")
        else:
            click.echo(f"⚠️ Key file not found or unreadable for '{repo_name}'")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"⚠️ {str(e)}")
    except Exception as e:
        click.echo(f"⚠️ Failed to get key: {e}")
    except PermissionError as e:
        click.echo(f"🚫 Permission error: {e}")
    except RuntimeError as e:
        click.echo(f"❌ Git/Sync/Decryption error: {e}")

@cli.command(name="set-key")
@click.argument("repo_name")
@click.argument("key")
def set_key(repo_name, key):
    """
    Set the Fernet key for a specific repo. \n
    Usage: \n
        - gitenvy set-key <REPO_NAME> <KEY> \n
        Sets the Fernet key for the specified repo.
    """
    cm = ConfigManager()
    config = cm.load()
    repo_cfg = config['configs'].get(repo_name)
    if not repo_cfg:
        click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
        return
    try:
        cm.set_fernet_key(repo_name, key)
        click.echo(f"✅ Key updated for '{repo_name}'")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"⚠️ {str(e)}")
    except Exception as e:
        click.echo(f"⚠️ Failed to set key: {e}")
    except PermissionError as e:
        click.echo(f"🚫 Permission error: {e}")
    except RuntimeError as e:
        click.echo(f"❌ Git/Sync/Decryption error: {e}")

if __name__ == "__main__":
    cli()
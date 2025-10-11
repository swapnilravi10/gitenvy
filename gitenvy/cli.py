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
    """Initialize gitenvy by cloning the env repo and saving config."""

    config_builder = ConfigBuilder()
    config_name = config_builder.extract_repo_name(repo)
    path = os.path.expanduser(os.path.join(path, config_name))

    # Clone or pull the repo first
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
    Push .env file for a specific project and environment.
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

@cli.command(name="list")
@click.option("--repo-name", required=False, help="Name of the repo as in config")
@click.option("--project", required=False, help="Project name")
@click.option("--env", "--env-name", required=False, help="Environment name")
def list_config(repo_name, project, env):
    """
    List all repo names in your config in a tabular format, marking the default.
    If --repo-name is provided, list all projects in that repo.
    If --repo-name and --project are provided, list all envs in that project.
    If --repo-name, --project and --env-name are provided, list all versions in that env.
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
    Pull .env from git or a specific project and environment.
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

@cli.command(name="set-default")
@click.argument("repo_name")
def set_default(repo_name):
    cm = ConfigManager()
    config = cm.load()
    if repo_name not in config.get("configs", {}):
        click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
        return
    cm.set_default(repo_name)
    click.echo(f"✅ Default repo set to '{repo_name}'")

@cli.command(name="get-key")
@click.argument("repo_name")
def get_key(repo_name):
    cm = ConfigManager()
    config = cm.load()
    repo_cfg = config['configs'].get(repo_name)
    if not repo_cfg:
        click.echo(f"⚠️ Repo name '{repo_name}' not found in config.")
        return
    key_path = os.path.expanduser(repo_cfg['key_path'])
    if not os.path.exists(key_path):
        click.echo(f"⚠️ Key file '{key_path}' does not exist.")
        return
    try:
        with open(key_path, "r") as f:
            key = f.read().strip()
        click.echo(f"Key for repo '{repo_name}':\n{key}")
    except Exception as e:
        click.echo(f"⚠️ Failed to read key file: {e}")

if __name__ == "__main__":
    cli()
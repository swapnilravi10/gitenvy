import click
from dotenvy.env_manager import EnvManager
from dotenvy.config_manager import ConfigManager
import subprocess
import os
import json

DEFAULT_REPO_PATH = os.path.expanduser("~/.dotenvy/envs")

@click.group()
def cli():
    """dotenvy - manage environment variables securely."""
    pass

@cli.command()
@click.option("--repo", required=True, help="Git repo URL for storing envs")
@click.option("--path", default=DEFAULT_REPO_PATH, help="Local path to clone the repo")
def init(repo, path):
    """Initialize dotenvy by cloning the env repo and saving config."""
    path = os.path.expanduser(path)
    cm = ConfigManager()

    # Save config
    cm.save({"repo_url": repo, "repo_path": path})
    click.echo(f"Config saved: {repo} -> {path}")

    # Clone repo if not exists
    if not os.path.exists(path):
        subprocess.run(["git", "clone", repo, path], check=True)
        click.echo("Repo cloned successfully")
    else:
        git_dir = os.path.join(path, ".git")
        if os.path.exists(git_dir):
            click.echo("Repo path exists, pulling latest changes...")
            subprocess.run(["git", "-C", path, "pull"], check=True)
        else:
            click.echo("Warning: path exists but is not a git repo.")

@cli.command()
@click.option('--project', required=True, help='Project name')
@click.option('--env','--env-name', required=True, help='Environment name (e.g., dev, prod)')
@click.option("--repo-path", default=DEFAULT_REPO_PATH, help="Local git repo path to store encrypted envs")
def push(project, env, repo_path):
    """Push and encrypt the .env file for a specific project and environment."""
    manager = EnvManager(project, env, repo_path=repo_path)
    try:
        out_file = manager.push()
        click.echo(f"Encrypted .env file stored at: {out_file}")
    except FileNotFoundError as e:
        click.echo(str(e))

@cli.command()
@click.option("--project", required=True)
@click.option("--env", "--env-name", required=True)
@click.option("--repo-path", default=DEFAULT_REPO_PATH)
def list(project, env, repo_path):
    """List all versions of a project/env"""
    base_dir = os.path.join(repo_path, project, env)
    if not os.path.exists(base_dir):
        click.echo("No versions found")
        return

    versions = sorted([v for v in os.listdir(base_dir) if v.isdigit()])
    for v in versions:
        meta_file = os.path.join(base_dir, v, "metadata.json")
        if os.path.exists(meta_file):
            with open(meta_file) as f:
                meta = json.load(f)
            click.echo(f"Version {v}: updated by {meta['last_updated_by']} at {meta['last_updated_at']}")
        else:
            click.echo(f"Version {v}: metadata missing")

@cli.command()
@click.option("--project", required=True)
@click.option("--env", "--env-name", required=True)
@click.option("--version", default="latest", help="Version to pull")
@click.option("--out-path", default=".env", help="Where to save decrypted .env")
@click.option("--repo-path", default=DEFAULT_REPO_PATH)
def pull(project, env, version, out_path, repo_path):
    """Pull a version of .env from git and decrypt it locally"""
    manager = EnvManager(project, env, repo_path=repo_path)
    try:
        file_path = manager.pull(version=version, out_path=out_path)
        click.echo(f"✅ Decrypted .env saved to {file_path}")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"⚠️ {str(e)}")

if __name__ == "__main__":
    cli() 
import click
from gitenvy.env_manager import EnvManager
from gitenvy.config_manager import ConfigManager
import subprocess
import os
import json

DEFAULT_REPO_PATH = os.path.expanduser("~/.gitenvy/envs")

@click.group()
def cli():
    """gitenvy - manage environment variables securely."""
    pass

@cli.command()
@click.option("--repo", required=True, help="Git repo URL for storing envs")
@click.option("--path", default=DEFAULT_REPO_PATH, help="Local path to clone the repo")
def init(repo, path):
    """Initialize gitenvy by cloning the env repo and saving config."""
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
    """
    Push .env file for a specific project and environment. \n
    Usage: \n
        gitenvy push --project <PROJECT> --env <ENV> 
            Encrypts and pushes the .env file in the current directory to the specified project and environment.
    """
    manager = EnvManager(project, env, repo_path=repo_path)
    try:
        out_file = manager.push()
        click.echo(f"Encrypted .env file stored at: {out_file}")
    except FileNotFoundError as e:
        click.echo(str(e))

@cli.command()
@click.option("--project", required=False, help="Project name")
@click.option("--env", "--env-name", required=False, help="Environment name")
@click.option("--v","--version", required=False, help="Version")
@click.option("--repo-path", default=DEFAULT_REPO_PATH)
def list(project, env, repo_path):
    """
    List projects, envs, or versions. \n
    Usage: \n
        gitenvy list 
            List all projects.

        gitenvy list --project <PROJECT>
            List all environments under the specified project.

        gitenvy list --project <PROJECT> --env <ENV>
            List all versions for the specified environment in the project.

        gitenvy list --project <PROJECT> --env <ENV> --version
            List details of all versions

        gitenvy list --project <PROJECT> --env <ENV> --version <VERSION>
            List details of specific version (e.g., 1)

        gitenvy list --project <PROJECT> --env <ENV> --version latest
            List details of latest version (e.g., latest)

    Returns:
        Prints a list of projects, environments, or version metadata depending on the options provided.
    """
    manager = EnvManager(project or  "", env or "", repo_path=repo_path)
    try:
        if not project and not env:
            projects = manager.list_projects()
            if not projects:
                click.echo("⚠️ No projects found")
                return
            else:
                click.echo("📁 Projects:")
                for p in projects:
                    click.echo(f" - {p}")
                return
        elif project and not env:
            envs = manager.list_envs(project)
            if not envs:
                click.echo(f"⚠️ No environments found for project {project}")
                return
            else:
                click.echo(f"📁 Environments for project {project}:")
                for e in envs:
                    click.echo(f" - {e}")
                return
        elif project and env:
            versions = manager.list_versions()
            if not versions:
                click.echo("⚠️ No versions found")
                return
            for v in versions:
                if v["last_updated_by"] and v["last_updated_at"]:
                    click.echo(f"📄 Version {v['version']}: updated by {v['last_updated_by']} at {v['last_updated_at']}")
                else:
                    click.echo(f"📄 Version {v['version']}: metadata missing")
    except Exception as e:
        click.echo(f"⚠️ {str(e)}")
    

@cli.command()
@click.option("--project", required=True)
@click.option("--env", "--env-name", required=True)
@click.option("--version", default="latest", help="Version to pull")
@click.option("--out-path", default=".env", help="Where to save decrypted .env on machine")
@click.option("--repo-path", default=DEFAULT_REPO_PATH)
def pull(project, env, version, out_path, repo_path):
    """
    Pull .env from git or a specific project and environment. \n
    Usage: \n
        gitenvy pull --project <PROJECT> --env <ENV> 
            Pulls and decrypts the .env file for the specified project and environment. Default version is 'latest' and output path is './.env'.

        gitenvy pull --project <PROJECT> --env <ENV> --version <VERSION> --out-path <PATH>
            Optionally specify a version (default is 'latest') and output path (default is './.env').
    """
    manager = EnvManager(project, env, repo_path=repo_path)
    try:
        file_path = manager.pull(version=version, out_path=out_path)
        click.echo(f"✅ Decrypted .env saved to {file_path}")
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"⚠️ {str(e)}")

if __name__ == "__main__":
    cli() 
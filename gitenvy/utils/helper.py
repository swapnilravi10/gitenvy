import click
import os
from pathlib import Path
import json

def get_repo_table(config):
    repo_names = list(config.get("configs", {}).keys())
    default_repo = config.get("default")
    if not repo_names:
        click.echo("⚠️ No repos found in config.")
        return
    click.echo(f"{'repo-name':<30} {'default':<10}")
    click.echo("-" * 40)
    for name in repo_names:
        is_default = "✅" if name == default_repo else ""
        click.echo(f"{name:<30} {is_default:<10}")

def get_project_table(repo_path, repo_name):
    repo_path_obj = Path(os.path.expanduser(repo_path))
    if not repo_path_obj.exists():
        click.echo(f"⚠️ Repo path '{repo_path}' does not exist.")
        return
    projects = [p.name for p in repo_path_obj.iterdir() if p.is_dir() and not p.name.startswith('.git')]
    if not projects:
        click.echo(f"⚠️ No projects found in repo '{repo_name}'.")
        return
    click.echo(f"{'project-name':<30}")
    click.echo("-" * 30)
    for proj in projects:
        click.echo(f"{proj:<30}")

def get_env_table(repo_path, repo_name, project):
    project_path = Path(os.path.expanduser(repo_path)) / project
    if not project_path.exists():
        click.echo(f"⚠️ Project '{project}' not found in repo '{repo_name}'.")
        return
    envs = [p.name for p in project_path.iterdir() if p.is_dir() and not p.name.startswith('.git')]
    if not envs:
        click.echo(f"⚠️ No environments found in project '{project}'.")
        return
    click.echo(f"{'env-name':<30}")
    click.echo("-" * 30)
    for env in envs:
        click.echo(f"{env:<30}")

def get_version_table(repo_path, repo_name, project, env_name):
    env_path = Path(os.path.expanduser(repo_path)) / project / env_name
    if not env_path.exists():
        click.echo(f"⚠️ Environment '{env_name}' not found in project '{project}' of repo '{repo_name}'.")
        return

    version_dirs = [p for p in env_path.iterdir() if p.is_dir() and p.name.isdigit()]
    if not version_dirs:
        click.echo(f"⚠️ No versions found in environment '{env_name}' of project '{project}'.")
        return

    click.echo(f"{'version':<10}{'last_updated_by':<20}{'last_updated_at':<30}")
    click.echo("-" * 60)

    for version_dir in sorted(version_dirs, key=lambda x: int(x.name)):
        metadata_file = version_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            click.echo(f"{metadata.get('version', ''):<10}{metadata.get('last_updated_by', ''):<20}{metadata.get('last_updated_at', ''):<30}")
        else:
            click.echo(f"{version_dir.name:<10}{'(no metadata)':<20}")

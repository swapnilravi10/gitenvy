import click
from dotenvy.env_manager import EnvManager

@click.group()
def cli():
    """dotenvy - manage environment variables securely."""
    pass

@cli.command()
@click.option('--project', required=True, help='Project name')
@click.option('--env','--env-name', required=True, help='Environment name (e.g., dev, prod)')
@click.option("--repo-path", default=r"C:\Users\swapn\Documents\work\test", help="Local git repo path to store encrypted envs")
def push(project, env, repo_path):
    """Push and encrypt the .env file for a specific project and environment."""
    manager = EnvManager(project, env, repo_path=repo_path)
    try:
        out_file = manager.push()
        click.echo(f"Encrypted .env file stored at: {out_file}")
    except FileNotFoundError as e:
        click.echo(str(e))

if __name__ == "__main__":
    cli() 
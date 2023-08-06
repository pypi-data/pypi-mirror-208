import typer
from pureml.cli.puremlconfig import PureMLConfigYML
import typer
from rich import print
# from puretrainer.train import Trainer
import os
from dotenv import load_dotenv

load_dotenv()


import pureml.cli.auth as auth
import pureml.cli.secrets as secrets
import pureml.cli.orgs as orgs

app = typer.Typer(no_args_is_help=True)
app.add_typer(auth.app, name="auth")
app.add_typer(secrets.app, name="secrets")
app.add_typer(orgs.app, name="orgs")


def print_version(value: bool):
    if value:
        from pureml import __version__

        print(f"PureML SDK version: {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: bool = typer.Option(
        None, "--version", "-v", callback=print_version, is_eager=True
    ),
):
    """
    PureML CLI

    This is the official CLI for PureML.
    """


# init the config file
@app.command()
def init(
    silent: bool = typer.Option(
        False, "--silent", "-s", help="Run in silent mode"
    ),
    # repository: str = typer.Option(
    #     None, "--repository", "-r", help="The repository to use"
    # ),
    backend_url: str = typer.Option(
        None, "--backend-url", "-b", help="The backend url to use"
    ),
    frontend_url: str = typer.Option(
        None, "--frontend-url", "-f", help="The frontend url to use"
    ),
):
    """
    This command will initialize the puremlconfig.yaml file for your project
    """
    from pathlib import Path

    project_path = Path.cwd()

    puremlconfig = PureMLConfigYML(project_path / "puremlconfig.yaml")
    
    # check if the config file exists
    if puremlconfig.file.exists():
        print("A puremlconfig.yaml file already exists in this directory - aborting")
        return
    
    # if not silent, ask for the config values
    if not silent:
        print("Let's get started with the configuration of your project")

        # if not repository:
        #     repository = typer.prompt("Enter your preferred storage repository path [eg. file://pureml_data/]")
        # else:
        #     print(f"Using given repository: {repository}")

        isSelfHosted = typer.confirm("Are you using a self-hosted PureML instance?")

        if isSelfHosted:
            if not backend_url:
                backend_url = typer.prompt("Enter the backend url", default="http://localhost:8080/api/")
            else:
                print(f"Using given backend url: {backend_url}")
            
            if not frontend_url:
                frontend_url = typer.prompt("Enter the frontend url", default="http://localhost:3000/")
            else:
                print(f"Using given frontend url: {frontend_url}")
    else:
        # if not repository:
        #     print("Missing required arguments")
        #     return
        # print(f"Using given repository: {repository}")
        if backend_url:
            print(f"Using given backend url: {backend_url}")
        if frontend_url:
            print(f"Using given frontend url: {frontend_url}")
    
    # create the config file
    data = {
        # "repository": repository,
    }
    if backend_url:
        data["backend_url"] = backend_url
    if frontend_url:
        data["frontend_url"] = frontend_url
    puremlconfig.save(data)
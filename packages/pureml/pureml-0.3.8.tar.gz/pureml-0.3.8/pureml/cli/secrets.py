import os
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
import jwt
import requests
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from pureml.cli.helpers import get_auth_headers
from pureml.schema.backend import get_backend_base_url
from pureml.cli.puremlconfig import PureMLConfigYML
from pureml.components import get_org_id
from pureml.schema import BackendSchema, PathSchema, ContentTypeHeader


path_schema = PathSchema().get_instance()
backend_schema = BackendSchema().get_instance()
app = typer.Typer()


@app.callback()
def callback():
    """
    Manage organization secrets

    Use with add, show, delete option

    add - Adds new secret for any integration
    all - Gets all secret names for the organization
    show - Show all secrets of secret name
    delete - Delete secrets under secret name
    """


@app.command()
def add(
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    )
):
    """
    Add a new integration and it's secrets

    Usage:
    pureml secrets add
    """
    backend_base_url = get_backend_base_url(backend_url)

    # Show all integrations
    print()
    console = Console()
    table = Table("Integration Name", "Integration Id")
    for integration in backend_schema.INTEGRATIONS:
        table.add_row(backend_schema.INTEGRATIONS[integration]["name"], integration)
    console.print(table)
    print()

    # Get integration id
    integration_id: str = typer.prompt("Enter the integration id")
    if integration_id not in backend_schema.INTEGRATIONS.keys():
        print(f"[bold red]Invalid integration id {integration_id}[/bold red]")
        return

    # Get secret name
    secret_name: str = typer.prompt("Enter the secret name")
    if not secret_name:
        print("[bold red]Invalid secret name[/bold red]")
        return

    # Get secret keys and values according to integration
    secret_keys = backend_schema.INTEGRATIONS[integration_id]["secrets"]
    user_secrets = {}
    for secret_key in secret_keys:
        secret_value = typer.prompt(f"Enter the value for {secret_key}")
        if not secret_value:
            print(f"[bold red]Invalid value for {secret_key}[/bold red]")
            return
        user_secrets[secret_key] = secret_value

    # Add secret
    org_id = get_org_id()

    data = {}
    url_path = ""

    # match integration_id:
    if integration_id == "s3":
        # case "s3":
        data = {
            "access_key_id": user_secrets["access_key_id"],
            "access_key_secret": user_secrets["access_key_secret"],
            "bucket_location": user_secrets["bucket_location"],
            "bucket_name": user_secrets["bucket_name"],
            "secret_name": secret_name,
        }
        url_path = f"org/{org_id}/secret/s3/connect"
        # case "r2":
    elif integration_id == "r2":
        data = {
            "access_key_id": user_secrets["access_key_id"],
            "access_key_secret": user_secrets["access_key_secret"],
            "account_id": user_secrets["account_id"],
            "bucket_name": user_secrets["bucket_name"],
            "public_url": user_secrets["public_url"],
            "secret_name": secret_name,
        }
        url_path = f"org/{org_id}/secret/r2/connect"

    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.post(url, json=data, headers=headers)

    if response.ok:
        print(f"[bold green]Successfully added secrets for {secret_name}[/bold green]")

    else:
        print("[bold red]Unable to fetch secrets!")


@app.command()
def all(
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    )
):
    """
    Get all secret names for the organization

    Usage:
    pureml secrets all
    """
    backend_base_url = get_backend_base_url(backend_url)

    print()
    org_id = get_org_id()
    url_path = f"org/{org_id}/secret"
    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.get(url, headers=headers)

    if response.ok:
        secrets_all = response.json()["data"]
        if not secrets_all or len(secrets_all) == 0:
            print("[bold red]No secrets found[/bold red]")
            return
        console = Console()

        table = Table("Secret Name")
        for secret in secrets_all:
            table.add_row(secret)

        console.print(table)
        print()
    else:
        print("[bold red]Unable to fetch secrets!")


@app.command()
def show(
    secret_name: str = typer.Argument(..., case_sensitive=True),
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    ),
):
    """
    Shows the secrets under given secret name

    Usage:
    pureml secrets show "secret_name"
    """
    backend_base_url = get_backend_base_url(backend_url)

    print()
    org_id = get_org_id()
    url_path = f"org/{org_id}/secret/{secret_name}"
    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.get(url, headers=headers)

    if response.ok:
        secrets_all = response.json()["data"]
        if not secrets_all or len(secrets_all) == 0:
            print(f"[bold red]No secrets found for {secret_name}[/bold red]")
            return
        secrets_all = secrets_all[0]

        print()
        print(f"[bold green]{secret_name} secrets :")
        console = Console()

        table = Table("Key", "Value")
        for key, value in secrets_all.items():
            table.add_row(key, value)

        console.print(table)
        print()

    else:
        print("[bold red]Unable to fetch secrets!")


@app.command()
def delete(
    secret_name: str = typer.Argument(..., case_sensitive=True),
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    ),
):
    """
    Delete secrets using key

    Usage:
    purecli secrets delete "secret_name"
    """
    backend_base_url = get_backend_base_url(backend_url)

    # Ask for confirmation
    print()
    confirm = typer.confirm(
        f"Are you sure you want to delete the {secret_name} secrets?"
    )
    if not confirm:
        return

    # Delete secret
    org_id = get_org_id()
    url_path = f"org/{org_id}/secret/{secret_name}"
    url = urljoin(backend_base_url, url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    response = requests.delete(url, headers=headers)

    if response.ok:
        print(f"[bold green]Successfully deleted {secret_name} secrets[/bold green]")
    else:
        print("[bold red]Unable to delete secrets!")


if __name__ == "__main__":
    app()

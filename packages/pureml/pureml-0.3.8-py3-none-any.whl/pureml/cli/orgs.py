from typing import Dict, List
import requests
import typer
from rich import print
from rich.console import Console
from rich.table import Table
from urllib.parse import urljoin
from pureml.cli.helpers import get_auth_headers, save_auth
from pureml.schema import BackendSchema, PathSchema, ContentTypeHeader, AcceptHeader
from pureml.schema.backend import get_backend_base_url

path_schema = PathSchema().get_instance()
backend_schema = BackendSchema().get_instance()
app = typer.Typer()


@app.callback()
def callback():
    """
    Organization command

    Use with show or select option

    show - lists all the organizations\n
    select - select an organization
    """


@app.command()
def show(
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    )
):
    url_path = "org"
    url = urljoin(get_backend_base_url(backend_url), url_path)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)
    response = requests.get(url, headers=headers)
    if response.ok:
        print()
        print("[bold green] You are part of following Organizations!")
        org_all = response.json()["data"]
        console = Console()
        count = 0
        table = Table("Sr.No.", "Name", "Description")
        org_data = {}
        for org in org_all:
            count += 1
            table.add_row(str(count), org["org"]["name"], org["org"]["description"])
            org_data[count] = {"id": org["org"]["uuid"], "name": org["org"]["name"]}

        console.print(table)
        print()
        return count, org_data
    else:
        print("[bold red]Unable to get the list of organizations!")
        return None, None


@app.command()
def select(
    backend_url: str = typer.Option(
        "",
        "--backend-url",
        "-b",
        help="Backend URL for self-hosted or custom pureml backend instance",
    )
):
    print("[bold green] Select the Sr.No. of Organization")
    count, org_data = show(backend_url=backend_url)
    if count:
        sr_no = -1
        while int(sr_no) not in range(1, count + 1):
            sr_no: str = typer.prompt(
                "Enter your Sr.No. of Organization (1 .... " + str(count) + ")"
            )
            if int(sr_no) not in range(1, count + 1):
                print("[bold red]Invalid Sr.No. of Organization!")
        save_auth(org_id=org_data[int(sr_no)]["id"])
        selected_org_name = org_data[int(sr_no)]["name"]
        print(f"[green]Successfully linked to organization {selected_org_name}!")
    else:
        print("[bold red]Did not Select any organization!")
        return None


# Possibly useful for future commands
# Moved from auth.py
def check_org_status(headers: dict, base_url: str):
    """
    Headers: dict
        headers from get_auth_headers() invocation of parent function

    base_url: str
        base_url from get_backend_base_url() invocation of parent function
    """

    org_id: str = typer.prompt("Enter your Org Id")

    url_path = "org/id/{}".format(org_id)
    url = urljoin(base_url, url_path)

    response = requests.get(url, headers=headers)

    if response.ok:
        # print("[green]Organization Exists!")
        return org_id
    else:
        print("[red]Organization does not Exists!")
        return None

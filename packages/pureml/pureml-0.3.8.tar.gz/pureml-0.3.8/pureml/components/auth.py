from urllib.parse import urljoin
import requests
import json
from rich import print
from pureml.cli.auth import save_auth
from . import delete_token, get_api_token, get_org_id
from pureml.schema import BackendSchema

backend_schema = BackendSchema().get_instance()


def login(org_id: str, api_token: str) -> str:
    """The function takes in a user API token and logs in a user for a session.

    Parameters
    ----------
    api_token: str
        API Key of the token to be used for login

    """

    url_path_1 = "org/id/{}".format(org_id)
    url = urljoin(backend_schema.BASE_URL, url_path_1)

    if (
        api_token is None
        or org_id is None
        or api_token == ""
        or org_id == ""
    ):
        print("[red]Invalid credentials for login")
        return

    headers = {"X-Api-Key": api_token}

    response = requests.get(url, headers=headers)

    # print(response.text)
    if response.status_code == 200:

        response_text = response.text
        response_org_details = json.loads(response_text)["data"]

        # if response_org_details is not None:
        response_org_id = response_org_details[0]["uuid"]

        if response_org_id == org_id:
            print("[green]Valid Org Id and API token. Logged in successfully")
            save_auth(org_id=org_id, api_token=api_token)

        else:
            print("[orange]Valid Org Id and API token. Obtained different organization")

        # else:
        #     print('[green] Invalid Org Id and Access token')
    elif response.status_code == 403:
        print("[red]Invalid API token")
        # delete_token(True)
    elif response.status_code == 404:
        print("[red]Invalid Org Id")
        # delete_token(True)
    else:
        print("[red]Unable to obtain the organization details")
        # delete_token(True)

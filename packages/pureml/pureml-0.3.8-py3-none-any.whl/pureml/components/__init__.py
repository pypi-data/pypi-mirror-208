import os, json
from pureml.schema import PathSchema
from rich import print

path_schema = PathSchema().get_instance()


def get_token():
    """It checks if the token exists in the user's home directory. If it does, it returns the token. If it
    doesn't, it returns None

    Returns
    -------
        The token is being returned.
    """
    path = path_schema.PATH_USER_TOKEN
    # path = os.path.expanduser(path)

    if os.path.exists(path):
        creds = open(path, "r").read()

        creds_json = json.loads(creds)
        if "accessToken" in creds_json:
            token = creds_json["accessToken"]
            return token
    return


def get_api_token():
    """It checks if the api token exists in the user's home directory. If it does, it returns the api token id and key. If it
    doesn't, it returns None

    Returns
    -------
        The api token id and key is returned.
        Dictionary format: {"api_token": api_token}
    """
    path = path_schema.PATH_USER_TOKEN
    # path = os.path.expanduser(path)

    if os.path.exists(path):
        creds = open(path, "r").read()

        creds_json = json.loads(creds)
        if "api_token" in creds_json:
            api_token = creds_json["api_token"]
            return {
                "api_token": api_token
            }
    return


def delete_token(silent=False):
    """It checks if the token exists in the user's home directory. If it does, it deletes the token. If it
    doesn't, it returns None

    Returns
    -------
        The token is being returned.
    """
    path = path_schema.PATH_USER_TOKEN
    # path = os.path.expanduser(path)

    if os.path.exists(path):
        os.remove(path)
        if not silent:
            print(f"[bold green]Authentication token deleted!")
        return
    else:
        if not silent:
            print(f"[bold red]Authentication token does not exist! Please login")
        return


def get_org_id():
    """It checks if the org exists in the user's home directory. If it does, it returns the org. If it
    doesn't, it returns None

    Returns
    -------
        The org is being returned.

    """

    path = path_schema.PATH_USER_TOKEN

    path = os.path.expanduser(path)

    if os.path.exists(path):
        creds = open(path, "r").read()

        creds_json = json.loads(creds)

        if "org_id" in creds_json:
            org_id = creds_json["org_id"]
            # print(f"[bold green]Organization exists!")

            # print(org_id)
            return org_id
        
    print(f"[bold red]Organization id does not exist! Please login")
    return


def convert_values_to_string(logged_dict):

    for key in logged_dict:
        logged_dict[key] = str(logged_dict[key])

    return logged_dict

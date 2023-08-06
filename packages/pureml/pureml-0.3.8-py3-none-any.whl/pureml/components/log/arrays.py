import requests

from rich import print
from rich.syntax import Syntax

import os
import json


from urllib.parse import urljoin

from pureml.cli.helpers import get_auth_headers

from . import get_token, get_org_id

from pureml.schema import PathSchema, BackendSchema, ContentTypeHeader
from joblib import Parallel, delayed
from PIL import Image

path_schema = PathSchema().get_instance()
backend_schema = BackendSchema().get_instance()


def save_images(array):
    array_paths = {}
    for array_key, array_value in array.items():
        save_name = os.path.join(
            path_schema.PATH_ARRAY_DIR, ".".join(array_key, ".png")
        )

        data = Image.fromarray(array_value)
        data.save(save_name)

        array_paths[array_key] = array_paths

    return array_paths


def details(
    model_name: str, model_branch: str, model_version: str = "latest", name: str = ""
):
    """This function returns the details of the array for a given model

    Parameters
    ----------
    model_name : str
        The name of the model you want to get the array details for
    model_version: str
        The version of the model
    name : str
        The name of the array.

    """

    org_id = get_org_id()

    url = "org/{}/model/{}/branch/{}/version/{}/log".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        res_text = json.loads(response.text)

        if len(res_text) == 0:
            print("[bold yellow] No array have been found for the model")
            print(res_text)
            return
        else:
            print("[bold green]array have been found for the model")
            print(res_text)
            return res_text

    else:
        print("[bold red]Unable to obtain the array details")
        print(response.text)
        return


def add(
    array: str, model_name: str, model_branch: str, model_version: str = "latest"
) -> str:
    """`add` function takes in the path of the array, name of the array and the model name and
    registers the array

    Parameters
    ----------
    array : str
        The path to the array file.
    name : str
        The name of the array.
    model_name : str
        The name of the model you want to add array to.
    model_version: str
        The version of the model

    Returns
    -------
        The response is a JSON object

    """

    org_id = get_org_id()

    url = "org/{}/model/{}/branch/{}/version/{}/log".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    array_paths = save_images(arrays=array)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    files = {}
    for file_name, file_path in array_paths.items():

        if os.path.isfile(file_path):
            files[file_name] = open(file_path, "rb")
        else:
            print("[bold red] array", file_name, "does not exist at the given path")

    data = {"name_path_mapping": array_paths}

    response = requests.post(url, data=data, files=files, headers=headers)

    if response.status_code == 200:
        print(f"[bold green]arrays have been registered!")

    else:
        print(f"[bold red]arrays have not been registered!")
        print(response.text)

    return response.text


def fetch(
    model_name: str, model_branch: str, model_version: str = "latest", name: str = ""
):
    """It fetches the array from the server and stores it in the local directory

    Parameters
    ----------
    model_name : str
        The name of the model you want to fetch the array from.
    model_version: str
        The version of the model
    name : str
        The name of the array to be fetched. If not specified, all arrays will be fetched.

    Returns
    -------
        The response text is being returned.

    """

    org_id = get_org_id()

    def fetch_array(array_details: dict):

        url = array_details["location"]
        file_path_temp = array_details["path"]
        file_name = file_path_temp.split(os.path.sep)[-1]
        save_path = os.path.join(path_schema.PATH_ARRAY_DIR, file_name)
        print("save path", save_path)

        name_fetched = array_details["array"]

        headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

        print("array url", url)

        # response = requests.get(url, headers=headers)
        response = requests.get(url)

        print(response.status_code)

        if response.status_code == 200:
            print("[bold green] array {} has been fetched".format(name_fetched))

            save_dir = os.path.dirname(save_path)

            os.makedirs(save_dir, exist_ok=True)

            array_bytes = response.content

            open(save_path, "wb").write(array_bytes)

            print(
                "[bold green] array {} has been stored at {}".format(
                    name_fetched, save_path
                )
            )

            return response.text
        else:
            print("[bold red] Unable to fetch the array")

            return response.text

    array_details = details(
        model_name=model_name,
        model_branch=model_branch,
        name=name,
        model_version=model_version,
    )

    if array_details is None:
        return

    if type(array_details) is dict:

        res_text = fetch_array(array_details)

    elif type(array_details) is list:
        res_text = Parallel(n_jobs=-1)(
            delayed(fetch_array)(art_det) for art_det in array_details
        )

    return res_text


def delete(
    name: str, model_name: str, model_branch: str, model_version: str = "latest"
) -> str:
    """`delete()` deletes an array from a model

    Parameters
    ----------
    name : str
        The name of the array you want to delete.
    model_name : str
        The name of the model you want to delete the array from
    model_version: str
        The version of the model

    """

    org_id = get_org_id()

    url = "org/{}/model/{}/branch/{}/version/{}/log".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    # array_details = details(model_name=model_name, array=array)

    # if array_details is None:
    #     print('[bold red] Unable to find array details')
    #     return

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print(f"[bold green]array has been deleted")

    else:
        print(f"[bold red]Unable to delete array")

    return response.text

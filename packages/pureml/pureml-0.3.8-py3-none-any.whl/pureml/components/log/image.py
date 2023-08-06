from pathlib import Path
from typing import Optional
import jwt
import requests

# import typer
from rich import print
from rich.syntax import Syntax

import os
import json
import typing

from urllib.parse import urljoin

from pureml.cli.helpers import get_auth_headers

from . import get_token, get_org_id

from pureml.schema import PathSchema, BackendSchema, ContentTypeHeader
from joblib import Parallel, delayed

path_schema = PathSchema().get_instance()
backend_schema = BackendSchema().get_instance()


def details(
    model_name: str, model_branch: str, model_version: str = "latest", name: str = ""
):
    """This function returns the details of the image for a given model

    Parameters
    ----------
    model_name : str
        The name of the model you want to get the image details for
    model_version: str
        The version of the model
    name : str
        The name of the image.

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
            print("[bold yellow] No image have been found for the model")
            print(res_text)
            return
        else:
            print("[bold green]image have been found for the model")
            print(res_text)
            return res_text

    else:
        print("[bold red]Unable to obtain the image details")
        print(response.text)
        return


def add(
    image: str, model_name: str, model_branch: str, model_version: str = "latest"
) -> str:
    """`add` function takes in the path of the image, name of the image and the model name and
    registers the image

    Parameters
    ----------
    image : str
        The path to the image file.
    name : str
        The name of the image.
    model_name : str
        The name of the model you want to add image to.
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

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    files = {}
    for file_name, file_path in image.items():

        if os.path.isfile(file_path):
            files[file_name] = open(file_path, "rb")
        else:
            print("[bold red] image", file_name, "does not exist at the given path")

    data = {"name_path_mapping": image}

    response = requests.post(url, data=data, files=files, headers=headers)

    if response.status_code == 200:
        print(f"[bold green]images have been registered!")

    else:
        print(f"[bold red]images have not been registered!")
        print(response.text)

    return response.text


def fetch(
    model_name: str, model_branch: str, model_version: str = "latest", name: str = ""
):
    """It fetches the image from the server and stores it in the local directory

    Parameters
    ----------
    model_name : str
        The name of the model you want to fetch the image from.
    model_version: str
        The version of the model
    name : str
        The name of the image to be fetched. If not specified, all images will be fetched.

    Returns
    -------
        The response text is being returned.

    """

    org_id = get_org_id()

    def fetch_image(image_details: dict):

        url = image_details["location"]
        file_path_temp = image_details["path"]
        file_name = file_path_temp.split(os.path.sep)[-1]
        save_path = os.path.join(path_schema.PATH_IMAGE_DIR, file_name)
        print("save path", save_path)

        name_fetched = image_details["image"]

        headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

        print("image url", url)

        # response = requests.get(url, headers=headers)
        response = requests.get(url)

        print(response.status_code)

        if response.status_code == 200:
            print("[bold green] image {} has been fetched".format(name_fetched))

            save_dir = os.path.dirname(save_path)

            os.makedirs(save_dir, exist_ok=True)

            image_bytes = response.content

            open(save_path, "wb").write(image_bytes)

            print(
                "[bold green] image {} has been stored at {}".format(
                    name_fetched, save_path
                )
            )

            return response.text
        else:
            print("[bold red] Unable to fetch the image")

            return response.text

    image_details = details(
        model_name=model_name,
        model_branch=model_branch,
        name=name,
        model_version=model_version,
    )

    if image_details is None:
        return

    if type(image_details) is dict:

        res_text = fetch_image(image_details)

    elif type(image_details) is list:
        res_text = Parallel(n_jobs=-1)(
            delayed(fetch_image)(art_det) for art_det in image_details
        )

    return res_text


# def delete(
#     name: str, model_name: str, model_branch: str, model_version: str = "latest"
# ) -> str:
#     """`delete()` deletes an image from a model

#     Parameters
#     ----------
#     name : str
#         The name of the image you want to delete.
#     model_name : str
#         The name of the model you want to delete the image from
#     model_version: str
#         The version of the model

#     """

#     user_token = get_token()
#     org_id = get_org_id()

#     url = "org/{}/model/{}/branch/{}/version/{}/log".format(
#         org_id, model_name, model_branch, model_version
#     )
#     url = urljoin(backend_schema.BASE_URL, url)

#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Authorization": "Bearer {}".format(user_token),
#     }

#     # image_details = details(model_name=model_name, image=image)

#     # if image_details is None:
#     #     print('[bold red] Unable to find image details')
#     #     return

#     response = requests.delete(url, headers=headers)

#     if response.status_code == 200:
#         print(f"[bold green]image has been deleted")

#     else:
#         print(f"[bold red]Unable to delete image")

#     return response.text

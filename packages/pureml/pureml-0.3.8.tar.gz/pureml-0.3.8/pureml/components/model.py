import requests
from rich import print

import os
import json

from pureml.cli.helpers import get_auth_headers

from . import get_org_id
from pureml.schema import (
    ModelSchema,
    StorageSchema,
    ConfigKeys,
    ContentTypeHeader,
    AcceptHeader,
)
from pureml import save_model, load_model
from urllib.parse import urljoin
import joblib
from pureml.utils.hash import generate_hash_for_file
from pureml.utils.readme import load_readme
from pureml.utils.version_utils import parse_version_label
from pureml.utils.config import reset_config


config_keys = ConfigKeys
storage = StorageSchema().get_instance()


def init_branch(label):
    name, branch, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/{}/branch/create".format(org_id, name)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    data = {"model_name": name, "branch_name": branch}

    data = json.dumps(data)

    response = requests.post(url, data=data, headers=headers)

    if response.ok:
        print(f"[bold green]Branch has been created!")

        return True

    else:
        print(f"[bold red]Branch has not been created!")

        return False


def check_model_hash(hash: str, label: str):

    name, branch, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/{}/branch/{}/hash-status".format(org_id, name, branch)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    data = {"hash": hash, "branch": branch}

    data = json.dumps(data)

    response = requests.post(url, data=data, headers=headers)

    hash_exists = False

    if response.ok:
        hash_exists = response.json()["data"][0]

    return hash_exists


def branch_details(label: str):
    name, branch, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/{}/branch/{}".format(org_id, name, branch)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.get(url, headers=headers)
    # print(response.url)
    # print(response.text)

    if response.ok:
        # T-1161 standardize api response to contains Models as a list
        response_text = response.json()
        details = response_text["data"]
        # print(model_details)

        return details

    else:
        print(f"[bold red]Branch details details have not been found")
        return


def branch_status(label: str):

    details = branch_details(label=label)

    if details:
        return True
    else:
        return False


def branch_delete(label: str) -> str:
    name, branch, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/{}/branch/{}/delete".format(org_id, name, branch)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.delete(url, headers=headers)

    if response.ok:
        print(f"[bold green]Model branch has been deleted")

    else:
        print(f"[bold red]Unable to delete Model branch")

    return response.text


def branch_list(label: str) -> str:

    name, _, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/{}/branch".format(org_id, name)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.get(url, headers=headers)

    if response.ok:
        response_text = response.json()
        branch_list = response_text["data"]

        return branch_list

    else:
        print(f"[bold red]Unable to obtain the list of branches!")

    return response.text


def list():
    """This function will return a list of all the modelst

    Returns
    -------
        A list of all the models

    """

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/all".format(org_id)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.get(url, headers=headers)

    if response.ok:
        # print(f"[bold green]Obtained list of models")

        response_text = response.json()
        model_list = response_text["data"]
        # print(model_list)

        return model_list
    else:
        print(f"[bold red]Unable to obtain the list of models!")

    return


def init(label: str, readme: str = None):

    name, branch, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    if readme is None:
        readme = ModelSchema().PATH_MODEL_README

    file_content, file_type = load_readme(path=readme)

    branch_user = "dev" if branch is None else branch
    branch_main = "main"

    url = "org/{}/model/{}/create".format(org_id, name)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    data = {
        "name": name,
        "branch_names": [branch_main, branch_user],
        "readme": {"file_type": file_type, "content": file_content},
    }

    data = json.dumps(data)

    files = {"file": (readme, open(readme, "rb"), file_type)}

    response = requests.post(url, data=data, headers=headers)
    # response = requests.post(url, data=data, headers=headers, files=files)

    if response.ok:
        print(f"[bold green]Model has been created!")

        return True
    else:
        print(f"[bold red]Model has not been created!")

        return False


def register(
    model,
    label,
    is_empty: bool = False,
):

    name, branch, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    model_file_name = ".".join([name, "pkl"])
    model_path = os.path.join(model_schema.paths.PATH_MODEL_DIR, model_file_name)

    os.makedirs(model_schema.paths.PATH_MODEL_DIR, exist_ok=True)

    save_model(model, name, model_path=model_path)

    model_hash = generate_hash_for_file(
        file_path=model_path, name=name, branch=branch, is_empty=is_empty
    )

    model_exists = model_status(label)

    if not model_exists:
        model_created = init(label)
        print("model_created", model_created)
        if not model_created:
            print("[bold red] Unable to register the model")
            return False, model_hash, "latest"

    branch_exists = branch_status(label)
    print("branch_exists", branch_exists)

    if not branch_exists:
        branch_created = init_branch(label)
        print("branch_created", branch_created)

        if not branch_created:
            print("[bold red] Unable to register the model")
            return False, model_hash, "latest"

    model_exists_remote = check_model_hash(hash=model_hash, label=label)

    if model_exists_remote:
        print(f"[bold red]Model already exists. Not registering a new version!")
        return True, model_hash, "latest"
    else:
        url = "org/{}/model/{}/branch/{}/register".format(org_id, name, branch)
        url = urljoin(model_schema.backend.BASE_URL, url)

        headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

        files = {"file": (model_file_name, open(model_path, "rb"))}

        data = {
            "name": name,
            "branch": branch,
            "hash": model_hash,
            "is_empty": is_empty,
            "storage": storage.STORAGE,
        }

        response = requests.post(url, files=files, data=data, headers=headers)
        # print(response.request.headers)

        if response.ok:

            model_version = None

            # print(response.json())
            try:
                print(f"[bold green]Model has been registered!")

                model_version = response.json()["data"][0]["version"]
                print("Model Version: ", model_version)
                model_label = ":".join([label, model_version])
                print("Model label: ", model_label)

                # reset_config(key=config_keys.model.value)
            except Exception as e:
                print(
                    "[bold red] Incorrect json response. Model has not been registered"
                )
                print(e)

            return True, model_hash, model_version

        else:
            print(f"[bold red]Model has not been registered!")
            print(response.text)

        return False, model_hash, None


def model_status(label: str):

    name, _, _ = parse_version_label(label)

    model_details = details(label=label)

    if model_details:
        return True
    else:
        return False


def details(label: str):
    """It fetches the details of a model.

    Parameters
    ----------
    name : str
        The name of the model
    version: str
        The version of the model
    Returns
    -------
        The details of the model.

    """

    name, _, _ = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/{}".format(org_id, name)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED,
        accept=AcceptHeader.APP_JSON,
    )

    response = requests.get(url, headers=headers)
    # print(response.url)
    # print(response.text)

    if response.ok:
        # print(f"[bold green]Model details have been fetched")
        response_text = response.json()
        model_details = response_text["data"][0]
        # print(model_details)

        return model_details

    else:
        print(f"[bold red]Model details have not been found")
        return


def version_details(label: str):
    """It fetches the details of a model.

    Parameters
    ----------
    name : str
        The name of the model
    version: str
        The version of the model
    Returns
    -------
        The details of the model.

    """

    name, branch, version = parse_version_label(label)

    org_id = get_org_id()
    model_schema = ModelSchema()

    url = "org/{}/model/{}/branch/{}/version/{}".format(org_id, name, branch, version)
    url = urljoin(model_schema.backend.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.get(url, headers=headers)

    if response.ok:
        # print(f"[bold green]Model Version details have been fetched")
        response_text = response.json()
        model_details = response_text["data"][0]
        # print(model_details)

        return model_details

    else:
        print(f"[bold red]Model details have not been found")
        return


def fetch(label: str):
    """This function fetches a model from the server and returns it as a `Model` object

    Parameters
    ----------
    name : str, optional
        The name of the model you want to fetch.
    version: str
        The version of the model

    Returns
    -------
        The model is being returned.

    """

    name, branch, version = parse_version_label(label)

    org_id = get_org_id()

    model_details = version_details(label=label)

    if model_details is None:
        print(f"[bold red]Unable to fetch Model version")
        return

    is_empty = model_details["is_empty"]

    if is_empty:
        print("[bold orange]Model file is not registered to the version")
        return

    # storage_path = model_details["path"]["source_path"]
    # storage_source_type = model_details["path"]["source_type"]["public_url"]

    # model_url = urljoin(storage_source_type, storage_path)

    model_url = model_details["path"]

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.get(model_url)

    if response.ok:
        model_bytes = response.content
        open("temp_model.pure", "wb").write(model_bytes)

        model = load_model(model_path="temp_model.pure")

        # print(f"[bold green]Model version has been fetched")
        return model
    else:
        print(f"[bold red]Unable to fetch Model version")
        # print(response.status_code)
        # print(response.text)
        # print(response.url)
        return


# def delete(label: str) -> str:
#     """This function deletes a model from the project

#     Parameters
#     ----------
#     name : str
#         The name of the model you want to delete
#     version : str
#         The version of the model to delete.

#     """

#     name, _, _ = parse_version_label(label)

#     user_token = get_token()
#     org_id = get_org_id()
#     model_schema = ModelSchema()

#     url = "org/{}/model/{}/delete".format(org_id, name)
#     url = urljoin(model_schema.backend.BASE_URL, url)

#     headers = {
#         "Content-Type": ContentTypeHeader.APP_FORM_URL_ENCODED.value,
#         "Authorization": "Bearer {}".format(user_token),
#     }

#     response = requests.delete(url, headers=headers)

#     if response.ok:
#         print(f"[bold green]Model has been deleted")

#     else:
#         print(f"[bold red]Unable to delete Model")

#     return response.text


def serve_model():
    pass

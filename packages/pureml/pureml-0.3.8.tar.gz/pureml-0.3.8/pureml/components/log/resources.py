import json
import os
from urllib.parse import urljoin

import numpy as np
import requests
from joblib import Parallel, delayed
from pureml.cli.helpers import get_auth_headers

from pureml.utils.pipeline import add_resource_to_config
from pureml.utils.resources import zip_content, unzip_content
from pureml.schema import (
    PathSchema,
    BackendSchema,
    StorageSchema,
    LogSchema,
    PredictSchema,
    ConfigKeys,
    AcceptHeader,
    ContentTypeHeader,
)
from rich import print
from . import get_org_id

from pureml.utils.version_utils import parse_version_label
from pureml.utils.config import reset_config


path_schema = PathSchema().get_instance()
predict_schema = PredictSchema()
backend_schema = BackendSchema().get_instance()
post_key_resources = LogSchema().key.resources.value
config_keys = ConfigKeys
storage = StorageSchema().get_instance()


def post_resource(path, model_name: str, model_branch: str, model_version: str):
    org_id = get_org_id()

    url = "org/{}/model/{}/branch/{}/version/{}/logfile".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    try:
        zip_content(src_path=path, dst_path=predict_schema.PATH_RESOURCES)
    except Exception as e:
        print(e)

    if not os.path.exists(predict_schema.PATH_RESOURCES):
        print(f"[bold red]Unable to zip the resource!")
        return

    file_paths = {post_key_resources: path}
    files = [("file", (post_key_resources, open(predict_schema.PATH_RESOURCES, "rb")))]

    data = {
        "data": file_paths,
        "key": post_key_resources,
        "storage": storage.STORAGE,
    }

    # data = json.dumps(data)

    response = requests.post(url, data=data, files=files, headers=headers)

    if response.ok:
        print(f"[bold green]resource has been registered!")
        reset_config(key=config_keys.resource.value)

    else:
        print(f"[bold red]resource has not been registered!")

    return response


def add(
    label: str = None,
    path: str = None,
) -> str:

    model_name, model_branch, model_version = parse_version_label(label)

    add_resource_to_config(
        values=path,
        model_name=model_name,
        model_branch=model_branch,
        model_version=model_version,
    )

    if (
        model_name is not None
        and model_version is not None
        and model_version is not None
    ):
        response = post_resource(
            path=path,
            model_name=model_name,
            model_branch=model_branch,
            model_version=model_version,
        )

        print(response.text)

    # return response.text


def details(label: str):
    model_name, model_branch, model_version = parse_version_label(label)
    org_id = get_org_id()

    url = "org/{}/model/{}/branch/{}/version/{}/log".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    response = requests.get(url, headers=headers)

    if response.ok:
        # T-1161 standardize api response to contains Models as a list
        response_text = response.json()
        details = response_text["data"]

        # print(model_details)

        return details

    else:
        print(f"[bold red]Unable to fetch resource!")
        return


def fetch(label: str):
    model_name, model_branch, model_version = parse_version_label(label)

    org_id = get_org_id()

    def fetch_resource(file_details):

        file_name, url = file_details

        save_path = os.path.join(path_schema.PATH_PREDICT_DIR, file_name)
        # print("save path", save_path)

        headers = get_auth_headers(
            content_type=ContentTypeHeader.APP_FORM_URL_ENCODED,
            accept=AcceptHeader.APP_JSON,
        )

        # print("resorce url", url)

        # response = requests.get(url, headers=headers)
        response = requests.get(url)

        # print(response.status_code)

        if response.ok:
            print("[bold green] resource {} has been fetched".format(file_name))

            save_dir = os.path.dirname(save_path)

            os.makedirs(save_dir, exist_ok=True)

            resource_bytes = response.content

            open(save_path, "wb").write(resource_bytes)
            unzip_content(save_path, path_schema.PATH_PREDICT_DIR)

            print(
                "[bold green] resource {} has been stored at {}".format(
                    file_name, save_path
                )
            )

            return response.text
        else:
            print("[bold red] Unable to fetch the resource")

            return response.text

    resource_details = details(label=label)
    # print("resource_details", resource_details)

    if resource_details is None:
        return

    # pred_urls = give_resource_urls(details=resource_details)
    pred_urls = give_resource_url(details=resource_details, key=post_key_resources)

    if len(pred_urls) == 1:

        res_text = fetch_resource(pred_urls[0])

    else:
        res_text = Parallel(n_jobs=-1)(
            delayed(fetch_resource)(pred_url) for pred_url in pred_urls
        )


def give_resource_url(details, key: str):
    resource_paths = []
    # file_url = None
    source_path = None
    file_url = None
    # print(details)

    if details is not None:

        for det in details:
            # print(det["key"])
            if det["key"] == key:
                source_path = det["key"]
                file_url = det["data"]
                source_path = ".".join([source_path, "zip"])
                # source_path = os.path.join(path_schema.PATH_PREDICT_DIR, source_path)
                resource_paths.append([source_path, file_url])

                # print(source_path, file_url)

                return resource_paths
    print("[bold red] Unable to find the resource")

    return resource_paths

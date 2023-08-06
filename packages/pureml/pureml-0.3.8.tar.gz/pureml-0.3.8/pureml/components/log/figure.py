import json
import os
from urllib.parse import urljoin

import numpy as np
import requests
from joblib import Parallel, delayed
from PIL import Image
from pureml.cli.helpers import get_auth_headers

from pureml.utils.pipeline import add_figures_to_config
from pureml.schema import (
    PathSchema,
    BackendSchema,
    StorageSchema,
    LogSchema,
    ConfigKeys,
    AcceptHeader,
    ContentTypeHeader,
)
from rich import print
from . import get_org_id

from pureml.utils.version_utils import parse_version_label
from pureml.utils.config import reset_config


path_schema = PathSchema().get_instance()
backend_schema = BackendSchema().get_instance()
post_key_figure = LogSchema().key.figure.value
config_keys = ConfigKeys
storage = StorageSchema().get_instance()


def save_images(figure):

    os.makedirs(path_schema.PATH_FIGURE_DIR, exist_ok=True)
    figure_paths = {}
    for figure_key, figure_value in figure.items():
        if figure_key.rsplit(".", 1)[-1] == "png":
            save_name = figure_key
        else:
            save_name = os.path.join(
                path_schema.PATH_FIGURE_DIR, ".".join([figure_key, "png"])
            )

        canvas = figure_value.canvas
        canvas.draw()
        data = np.frombuffer(canvas.tostring_rgb(), dtype=np.uint8)
        rgb_array = data.reshape(canvas.get_width_height()[::-1] + (3,))

        data = Image.fromarray(rgb_array)
        data.save(save_name)

        figure_paths[figure_key] = save_name

    return figure_paths


def post_figures(figure_paths, model_name: str, model_branch: str, model_version: str):
    org_id = get_org_id()

    # print('figure_paths', figure_paths)

    url = "org/{}/model/{}/branch/{}/version/{}/logfile".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    files = []
    for file_name, file_path in figure_paths.items():
        # print("filename", file_name)

        if os.path.isfile(file_path):
            files.append(("file", (file_name, open(file_path, "rb"))))

        else:
            print("[bold red] figure", file_name, "does not exist at the given path")

    data = {
        "data": figure_paths,
        "key": "figure",
        "storage": storage.STORAGE,
    }

    # data = json.dumps(data)

    # try:

    response = requests.post(url, data=data, files=files, headers=headers)

    if response.ok:
        print(f"[bold green]Figures have been registered!")
        reset_config(key=config_keys.figure.value)

    else:
        print(f"[bold red]Figures have not been registered!")
        print(response.text)

    return response
    # except Exception as e:
    #     return


def add(label: str = None, figure: dict = None, file_paths: dict = None) -> str:
    """`add` function takes in the path of the figure, name of the figure and the model name and
    registers the figure

    Parameters
    ----------
    figure : dict
        Key is the figure name, value is the matplotlib figure object
    name : str
        The name of the figure.
    model_name : str
        The name of the model you want to add figure to.
    model_version: str
        The version of the model

    Returns
    -------
        The response is a JSON object

    """
    model_name, model_branch, model_version = parse_version_label(label)
    # print(model_name, model_branch, model_version)
    # print('file_paths', file_paths)
    # print('figure', figure)

    if file_paths is None:
        file_paths = save_images(figure)
        # print('figre paths', figure_paths)

    add_figures_to_config(
        values=file_paths,
        model_name=model_name,
        model_branch=model_branch,
        model_version=model_version,
    )

    if (
        model_name is not None
        and model_version is not None
        and model_version is not None
    ):
        response = post_figures(
            figure_paths=file_paths,
            model_name=model_name,
            model_branch=model_branch,
            model_version=model_version,
        )

        # print(response.text)

    # return response.text


def details(label: str):
    model_name, model_branch, model_version = parse_version_label(label)
    org_id = get_org_id()

    url = "org/{}/model/{}/branch/{}/version/{}/log".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

    response = requests.get(url, headers=headers)

    if response.ok:
        # T-1161 standardize api response to contains Models as a list
        response_text = response.json()
        details = response_text["data"]

        # print(model_details)

        return details

    else:
        print(f"[bold red]Unable to fetch Figure!")
        return


def fetch(label: str, key: str):
    """It fetches the figure from the server and stores it in the local directory

    Parameters
    ----------
    model_name : str
        The name of the model you want to fetch the figure from.
    model_version: str
        The version of the model
    name : str
        The name of the figure to be fetched. If not specified, all figures will be fetched.

    Returns
    -------
        The response text is being returned.

    """
    model_name, model_branch, model_version = parse_version_label(label)

    org_id = get_org_id()

    def fetch_figure(file_details):

        file_name, url = file_details

        save_path = os.path.join(path_schema.PATH_FIGURE_DIR, file_name)
        # print("save path in fetching", save_path)

        headers = get_auth_headers(content_type=ContentTypeHeader.APP_FORM_URL_ENCODED)

        # print("figure url", url)

        # response = requests.get(url, headers=headers)
        response = requests.get(url)

        # print(response.status_code)

        if response.ok:
            print("[bold green] figure {} has been fetched".format(file_name))

            save_dir = os.path.dirname(save_path)

            os.makedirs(save_dir, exist_ok=True)

            figure_bytes = response.content

            open(save_path, "wb").write(figure_bytes)

            print(
                "[bold green] figure {} has been stored at {}".format(
                    file_name, save_path
                )
            )

            return response.text
        else:
            print("[bold red] Unable to fetch the figure")

            return response.text

    figure_details = details(label=label)

    if figure_details is None:
        return

    # fig_urls = give_fig_urls(details=figure_details)
    fig_urls = give_fig_url(details=figure_details, key=key)

    if len(fig_urls) == 1:

        res_text = fetch_figure(fig_urls[0])

    else:
        res_text = Parallel(n_jobs=-1)(
            delayed(fetch_figure)(fig_url) for fig_url in fig_urls
        )

    # return res_text


def give_fig_url(details, key: str):
    fig_paths = []
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
                source_path = ".".join([source_path, "jpg"])
                # source_path = os.path.join(path_schema.PATH_FIGURE_DIR, source_path)
                fig_paths.append([source_path, file_url])

                # print(source_path, file_url)

                return fig_paths
    print("[bold red] Unable to find the figure")

    return fig_paths


# def give_fig_urls(details):

#     fig_paths = None

#     if details is not None:

#         details = details[0]["data"]
#         if "figure" in details.keys():
#             fig_paths = []

#             fig_details_all = details["figure"]

#             for fig_key, path in fig_details_all.items():
#                 source_path = fig_details_all[fig_key]["path"]["source_path"]
#                 source_url = fig_details_all[fig_key]["path"]["source_type"][
#                     "public_url"
#                 ]
#                 file_url = urljoin(source_url, source_path)
#                 fig_paths.append([source_path, file_url])

#     return fig_paths


# def delete(name:str, model_name:str,  model_version:str='latest') -> str:
#     '''`delete()` deletes an figure from a model

#     Parameters
#     ----------
#     name : str
#         The name of the figure you want to delete.
#     model_name : str
#         The name of the model you want to delete the figure from
#     model_version: str
#         The version of the model

#     '''

#     user_token = get_token()
#     org_id = get_org_id()

#     url_path_1 = '{}/project/{}/model/{}/{}/figure/{}/delete'.format(org_id, project_id, model_name, model_version, name)
#     url = urljoin(BASE_URL, url_path_1)


#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Authorization': 'Bearer {}'.format(user_token)
#     }


#     # figure_details = details(model_name=model_name, figure=figure)

#     # if figure_details is None:
#     #     print('[bold red] Unable to find figure details')
#     #     return


#     response = requests.delete(url, headers=headers)


#     if response.status_code == 200:
#         print(f"[bold green]figure has been deleted")

#     else:
#         print(f"[bold red]Unable to delete figure")

#     return response.text

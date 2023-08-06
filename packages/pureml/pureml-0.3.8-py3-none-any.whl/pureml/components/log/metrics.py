import json
from urllib.parse import urljoin

import requests
from pureml.cli.helpers import get_auth_headers
from pureml.schema import BackendSchema, LogSchema, ConfigKeys, ContentTypeHeader
from pureml.utils.log_utils import merge_step_with_value
from pureml.utils.pipeline import add_metrics_to_config
from rich import print

from . import convert_values_to_string, get_org_id
from pureml.utils.version_utils import parse_version_label
from pureml.utils.config import reset_config


backend_schema = BackendSchema().get_instance()
post_key_predict = LogSchema().key.metrics.value
config_keys = ConfigKeys


def post_metrics(metrics, model_name: str, model_branch: str, model_version: str):

    org_id = get_org_id()

    url = "org/{}/model/{}/branch/{}/version/{}/log".format(
        org_id, model_name, model_branch, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=ContentTypeHeader.ALL)

    metrics = json.dumps(metrics)
    data = {"data": metrics, "key": post_key_predict}

    data = json.dumps(data)

    response = requests.post(url, data=data, headers=headers)

    if response.ok:
        print(f"[bold green]Metrics have been registered!")
        reset_config(key=config_keys.metrics.value)

    else:
        print(f"[bold red]Metrics have not been registered!")

    return response


def add(
    metrics,
    label: str = None,
    step=1,
) -> str:
    """`add()` takes a dictionary of metrics and a model name as input and returns a string

    Parameters
    ----------
    metrics
        a dictionary of metrics
    model_name : str
        The name of the model you want to add metrics to.
    model_version: str
        The version of the model

    Returns
    -------
        The response.text is being returned.

    """
    model_name, model_branch, model_version = parse_version_label(label)

    metrics = convert_values_to_string(logged_dict=metrics)
    # metrics = merge_step_with_value(values_dict=metrics, step=step)

    add_metrics_to_config(
        values=metrics,
        model_name=model_name,
        model_branch=model_branch,
        model_version=model_version,
    )

    if (
        model_name is not None
        and model_branch is not None
        and model_version is not None
    ):
        response = post_metrics(
            metrics=metrics,
            model_name=model_name,
            model_branch=model_branch,
            model_version=model_version,
        )

        # return response.text

    # return


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
        print(f"[bold red]Unable to fetch logs!")
        return


def get_value_from_log(details, key_log=post_key_predict, key=None):
    value = None
    if details is not None:
        # print(details)

        for det in details:
            # print(det)
            # print(det["key"])
            if det["key"] == key_log:
                value = det["data"]
                # print(value)
                value = json.loads(value)

                if key is not None:
                    if key in value.keys():
                        value = value[key]
                    else:
                        print(
                            "[bold red]{} : {} is not available for the model!".format(
                                key_log, key
                            )
                        )

                return value

    print("[bold red] Unable to find the {}".format(key))

    return value


def fetch(label: str, metric: str = None) -> str:
    """This function fetches the metrics of a model

    Parameters
    ----------
    model_name : str
        The name of the model you want to fetch metrics for.
    model_version: str
        The version of the model
    metric : str
        The metric you want to fetch. If you want to fetch all the metrics, leave this parameter empty.

    Returns
    -------
        The metrics that are fetched

    """

    metric_details = details(label=label)

    if metric_details:

        metrics = get_value_from_log(
            details=metric_details, key_log=post_key_predict, key=metric
        )

        return metrics

    return


# def delete(metric: str, label: str) -> str:
#     """This function deletes a metric from a model

#     Parameters
#     ----------
#     model_name : str
#         The name of the model you want to delete the metric from
#     metric : str
#         The name of the metric to delete
#     model_version: str
#         The version of the model

#     """
#     model_name, model_branch, model_version = parse_version_label(label)

#     user_token = get_token()
#     org_id = get_org_id()
#     log_schema = LogSchema()

#     url = "org/{}/model/{}/branch/{}/version/{}/log/delete".format(
#         org_id, model_name, model_branch, model_version
#     )
#     url = urljoin(log_schema.backend.BASE_URL, url)

#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Authorization": "Bearer {}".format(user_token),
#     }

#     response = requests.delete(url, headers=headers)

#     if response.status_code == 200:
#         print(f"[bold green]Metric has been deleted")

#     else:
#         print(f"[bold red]Unable to delete Metric")

#     return response.text

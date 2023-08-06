import typing
import numpy as np
import matplotlib.pyplot as plt
from . import metrics as pure_metrics
from . import params as pure_params
from . import figure as pure_figure
from . import predict as pure_predict
from . import pip_requirement as pure_pip_req
from pureml.utils.version_utils import parse_version_label
from pureml.schema import PathSchema, BackendSchema, LogSchema
import requests
from urllib.parse import urljoin
from . import get_org_id

path_schema = PathSchema().get_instance()
backend_schema = BackendSchema().get_instance()

post_keys = LogSchema().key


def log(label: str = None, metrics=None, params=None, step=1, **kwargs):

    if metrics is not None:
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["metrics"] = metrics.copy()

        func_params["step"] = step

        pure_metrics.add(**func_params)

    if params is not None:
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["params"] = params.copy()

        func_params["step"] = step

        pure_params.add(**func_params)

    if post_keys.figure.value in kwargs.keys():
        figure = kwargs[post_keys.figure.value]
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["figure"] = figure.copy()
        # func_params['step']  = step

        pure_figure.add(**func_params)

    if post_keys.predict.value in kwargs.keys():
        predict = kwargs[post_keys.predict.value]
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["path"] = predict

        pure_predict.add(**func_params)

    if post_keys.requirements.value in kwargs.keys():
        requirement = kwargs[post_keys.requirements.value]
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["path"] = requirement

        pure_pip_req.add(**func_params)

from .config import load_config, save_config
from .hash import generate_hash_for_dict, generate_hash_for_function
from .source_code import get_source_code
import os
import shutil
from .log_utils import update_step_dict
import time
from pureml.schema import ConfigKeys
from datetime import datetime

config_keys = ConfigKeys


def add_load_data_to_config(name, description=None, func=None, hash=""):

    config = load_config()
    code = ""
    if func is not None:
        try:
            code = get_source_code(func)
            hash = generate_hash_for_function(func)
        except Exception as e:
            print("Unable to get load_data source code")
            print(e)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.load_data.value] = {
        "name": name,
        "desc": str(description),
        "time": current_datetime,
        "hash": hash,
        "type": config_keys.load_data.value,
        "code": code,
    }

    save_config(config=config)


def add_transformer_to_config(name, description=None, func=None, hash="", parent=None):

    config = load_config()
    # print(config)
    position = len(config[config_keys.transformer.value]) + 1

    if parent is None:
        if position == 1:

            if len(config[config_keys.load_data.value]) != 0:
                parent = config[config_keys.load_data.value]["name"]

        else:
            transformer_previous = config[config_keys.transformer.value][position - 1]
            parent = transformer_previous["name"]

    code = ""
    if func is not None:
        try:
            code = get_source_code(func)
            hash = generate_hash_for_function(func)
        except Exception as e:
            print("Unable to get transformer source code")
            print(e)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.transformer.value][position] = {
        "name": name,
        "desc": str(description),
        "time": current_datetime,
        "hash": hash,
        "type": config_keys.transformer.value,
        "parent": parent,
        "code": code,
    }
    # print('saveing configuration for ', name)
    save_config(config=config)


def add_dataset_to_config(
    name, branch, description=None, func=None, hash="", version="", parent=None
):

    config = load_config()

    if parent is None:

        if len(config[config_keys.transformer.value]) != 0:
            config_transformer = config[config_keys.transformer.value]
            transformer_last = list(config_transformer.values())[-1]
            parent = transformer_last["name"]

    code = ""
    if func is not None:
        try:
            code = get_source_code(func)
            hash = generate_hash_for_function(func)
        except Exception as e:
            print("Unable to get dataset source code")
            print(e)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.dataset.value] = {
        "name": name,
        "desc": str(description),
        "time": current_datetime,
        "branch": branch,
        "hash": hash,
        "type": config_keys.dataset.value,
        "version": version,
        "parent": parent,
        "code": code,
    }

    save_config(config=config)


def add_model_to_config(name, branch, description=None, func=None, hash="", version=""):
    # name = ''
    # hash = ''
    # version = ''

    config = load_config()

    code = ""
    if func is not None:
        try:
            code = get_source_code(func)
            hash = generate_hash_for_function(func)
        except Exception as e:
            print("Unable to get model source code")
            print(e)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    # Empty hash is passed to create the empty model with just model name the first time
    # Complete hash is passed to create the model with all the details in the second time
    if hash == "":
        position = len(config[config_keys.model.value]) + 1

        config[config_keys.model.value][position] = {
            "name": name,
            "desc": str(description),
            "time": current_datetime,
            "branch": branch,
            "hash": hash,
            "version": version,
            "code": code,
        }
    else:
        position = len(config[config_keys.model.value])
        model_name_position = config[config_keys.model.value][position]["name"]
        if model_name_position == name:
            config[config_keys.model.value][position]["branch"] = branch
            config[config_keys.model.value][position]["hash"] = hash
            config[config_keys.model.value][position]["version"] = version
            config[config_keys.model.value][position]["code"] = code

    save_config(config=config)


def add_metrics_to_config(
    values, model_name=None, model_branch=None, model_version=None, func=None
):
    config = load_config()

    if model_name is None:
        model_name, model_branch, model_version, model_hash = get_model_latest(
            config=config
        )

    if len(config[config_keys.metrics.value]) != 0:
        metric_values = config[config_keys.metrics.value]["values"]
        # metric_values = update_step_dict(metric_values, values)
        metric_values.update(values)
        # print('default',metric_values)
    else:
        metric_values = values

        # print('not default',metric_values)

    hash = generate_hash_for_dict(values=metric_values)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.metrics.value].update(
        {
            "values": metric_values,
            "hash": hash,
            "model_name": model_name,
            "model_branch": model_branch,
            "model_version": model_version,
            "time": current_datetime,
        }
    )

    save_config(config=config)


def load_metrics_from_config():

    config = load_config()
    try:
        metrics = config[config_keys.metrics.value]["values"]
    except Exception as e:
        # print(e)
        print("No metrics are found in config")
        metrics = {}

    return metrics


def add_params_to_config(
    values, model_name=None, model_branch=None, model_version=None, func=None
):
    config = load_config()

    if model_name is None:
        model_name, model_branch, model_version, model_hash = get_model_latest(
            config=config
        )

    if len(config[config_keys.params.value]) != 0:
        param_values = config[config_keys.params.value]["values"]
        # param_values = update_step_dict(param_values, values)
        param_values.update(values)
    else:
        param_values = values

    hash = generate_hash_for_dict(values=param_values)
    # print("params", model_version)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.params.value].update(
        {
            "values": param_values,
            "hash": hash,
            "model_name": model_name,
            "model_branch": model_branch,
            "model_version": model_version,
            "time": current_datetime,
        }
    )

    save_config(config=config)


def load_params_from_config():

    config = load_config()
    try:
        metrics = config[config_keys.params.value]["values"]
    except Exception as e:
        # print(e)
        print("No params are found in config")
        metrics = {}

    return metrics


def add_figures_to_config(
    values, model_name=None, model_branch=None, model_version=None, func=None
):
    config = load_config()

    if model_name is None:
        model_name, model_branch, model_version, model_hash = get_model_latest(
            config=config
        )

    if len(config[config_keys.figure.value]) != 0:
        figure_values = config[config_keys.figure.value]["values"]
        figure_values.update(values)
    else:
        figure_values = values

    hash = generate_hash_for_dict(values=figure_values)
    # print("figures", model_version)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.figure.value].update(
        {
            "values": figure_values,
            "hash": hash,
            "model_name": model_name,
            "model_branch": model_branch,
            "model_version": model_version,
            "time": current_datetime,
        }
    )

    save_config(config=config)


def load_figures_from_config():

    config = load_config()
    try:
        figures = config[config_keys.figure.value]["values"]
    except Exception as e:
        # print(e)
        print("No figures are found in config")
        figures = {}

    return figures


def add_pred_to_config(
    values, model_name=None, model_branch=None, model_version=None, func=None
):
    config = load_config()

    if model_name is None:
        model_name, model_branch, model_version, model_hash = get_model_latest(
            config=config
        )

    if len(config[config_keys.pred_function.value]) != 0:
        # pred_function_values = config["pred_function"]["values"]
        # pred_function_values.update(values)
        pred_function_values = values
    else:
        pred_function_values = values

    hash = generate_hash_for_dict(values=pred_function_values)
    # print("pred_function", model_version)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.pred_function.value].update(
        {
            "values": pred_function_values,
            "hash": hash,
            "model_name": model_name,
            "model_branch": model_branch,
            "model_version": model_version,
            "time": current_datetime,
        }
    )

    save_config(config=config)


def load_pred_from_config():

    config = load_config()
    try:
        pred_file = config[config_keys.pred_function.value]["values"]
    except Exception as e:
        # print(e)
        print("No pred_functions are found in config")
        pred_file = {}

    return pred_file


def add_pip_req_to_config(
    values, model_name=None, model_branch=None, model_version=None, func=None
):
    config = load_config()

    if model_name is None:
        model_name, model_branch, model_version, model_hash = get_model_latest(
            config=config
        )

    if len(config[config_keys.pip_requirement.value]) != 0:
        # pip_requirement_values = config["pip_requirement"]["values"]
        # pip_requirement_values.update(values)
        pip_requirement_values = values
    else:
        pip_requirement_values = values

    hash = generate_hash_for_dict(values=pip_requirement_values)
    # print("pred_function", model_version)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.pip_requirement.value].update(
        {
            "values": pip_requirement_values,
            "hash": hash,
            "model_name": model_name,
            "model_branch": model_branch,
            "model_version": model_version,
            "time": current_datetime,
        }
    )

    save_config(config=config)


def load_pip_req_from_config():

    config = load_config()
    try:
        pip_req_file = config[config_keys.pip_requirement.value]["values"]
    except Exception as e:
        # print(e)
        print("No pip_requirement are found in config")
        pip_req_file = {}

    return pip_req_file


def add_resource_to_config(
    values, model_name=None, model_branch=None, model_version=None, func=None
):
    config = load_config()

    if model_name is None:
        model_name, model_branch, model_version, model_hash = get_model_latest(
            config=config
        )

    if len(config[config_keys.resource.value]) != 0:
        # pip_requirement_values = config["pip_requirement"]["values"]
        # pip_requirement_values.update(values)
        pip_requirement_values = values
    else:
        pip_requirement_values = values

    hash = generate_hash_for_dict(values=pip_requirement_values)
    # print("pred_function", model_version)

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    config[config_keys.resource.value].update(
        {
            "values": pip_requirement_values,
            "hash": hash,
            "model_name": model_name,
            "model_branch": model_branch,
            "model_version": model_version,
            "time": current_datetime,
        }
    )

    save_config(config=config)


def load_resource_from_config():

    config = load_config()
    try:
        pip_req_file = config[config_keys.resource.value]["values"]
    except Exception as e:
        # print(e)
        print("No resource are found in config")
        pip_req_file = {}

    return pip_req_file


def add_artifacts_to_config(name, values, func):
    hash = ""
    version = ""
    config = load_config()

    model_name, model_branch, model_version, model_hash = get_model_latest(
        config=config
    )

    current_datetime = datetime.now()
    current_datetime = str(current_datetime.strftime("%d %b %Y, %H:%M"))

    position = len(config[config_keys.artifacts.value]) + 1
    config[config_keys.artifacts.value][position] = {
        "name": name,
        "hash": hash,
        "version": version,
        "model_name": model_name,
        "model_version": model_version,
        "time": current_datetime,
    }


def get_model_latest(config, version="latest"):
    config_model = config[config_keys.model.value]
    model_name = None
    model_version = None
    model_hash = None

    model_positions = list(config_model.keys())

    if len(model_positions) != 0:
        # print(model_positions)
        position = model_positions[-1]
        model_name = config_model[position]["name"]
        model_branch = config_model[position]["branch"]
        model_version = config_model[position]["version"]
        model_hash = config_model[position]["hash"]

    return model_name, model_branch, model_version, model_hash

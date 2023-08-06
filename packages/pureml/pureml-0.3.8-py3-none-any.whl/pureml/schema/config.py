from enum import Enum


class ConfigKeys(Enum):
    load_data = "load_data"
    transformer = "transformer"
    dataset = "dataset"
    model = "model"
    params = "params"
    metrics = "metrics"
    figure = "figure"
    artifacts = "artifacts"
    pred_function = "pred_function"
    pip_requirement = "pip_requirement"
    resource = "resource"

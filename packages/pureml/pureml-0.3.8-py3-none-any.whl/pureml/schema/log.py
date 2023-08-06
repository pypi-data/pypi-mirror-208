from pydantic import BaseModel
from .paths import PathSchema
from .backend import BackendSchema
import os
from enum import Enum


class LogKeys(Enum):
    metrics = "metrics"
    params = "params"
    figure = "figure"
    predict = "predict"
    requirements = "requirements"
    resources = "resources"


class LogSchema(BaseModel):
    paths: PathSchema = PathSchema().get_instance()
    backend: BackendSchema = BackendSchema().get_instance()
    key: LogKeys = LogKeys

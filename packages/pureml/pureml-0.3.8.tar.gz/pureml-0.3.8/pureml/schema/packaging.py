from pydantic import BaseModel
from .backend import BackendSchema

import typing
import os
from .paths import PathSchema


class FastAPISchema(BaseModel):
    paths: PathSchema = PathSchema().get_instance()
    PATH_FASTAPI_FILE = os.path.join(paths.PATH_PREDICT_DIR, "fastapi_server.py")
    PORT_FASTAPI = 8005  # Same port as docker server
    API_IP_HOST = "0.0.0.0"

    class Config:
        arbitrary_types_allowed = True


class DockerSchema(BaseModel):
    paths: PathSchema = PathSchema().get_instance()
    backend: BackendSchema = BackendSchema().get_instance()
    PATH_DOCKER_IMAGE = os.path.join(paths.PATH_PREDICT_DIR, "Dockerfile")
    PATH_DOCKER_CONFIG = os.path.join(paths.PATH_PREDICT_DIR, "DockerConfig.yaml")
    PORT_DOCKER = FastAPISchema().PORT_FASTAPI  # Same port as fastapi server
    PORT_HOST = 8000
    BASE_IMAGE_DOCKER = "python:3.8-slim"
    API_IP_DOCKER = FastAPISchema().API_IP_HOST
    API_IP_HOST = "0.0.0.0"

    class Config:
        arbitrary_types_allowed = True

from pydantic import BaseModel, root_validator
from .singleton import Singleton_BaseModel
import typing
import os
import typer

from pathlib import Path
from pureml.cli.puremlconfig import PureMLConfigYML


project_path = Path.cwd()
if Path.exists(project_path / "puremlconfig.yaml"):
    puremlconfig = PureMLConfigYML(project_path / "puremlconfig.yaml")
else:
    puremlconfig = None


def get_backend_base_url(backend_url: str = None):
    if (
        backend_url is not None
        and backend_url != ""
        and type(backend_url) == typer.Option
    ):
        # override backend url (command specific option)
        return backend_url
    if puremlconfig is not None:
        # user configured backend url (self-hosted or custom pureml backend instance)
        backend_url = (
            puremlconfig.data["backend_url"]
            if "backend_url" in puremlconfig.data
            else "https://pureml-development.up.railway.app/api/"
        )
    else:
        # default backend url (production cloud backend)
        backend_url = "https://pureml-development.up.railway.app/api/"
    return backend_url


def get_frontend_base_url(frontend_url: str = None):
    if (
        frontend_url is not None
        and frontend_url != ""
        and type(frontend_url) == typer.Option
    ):
        # override frontend url (command specific option)
        return frontend_url
    if puremlconfig is not None:
        # user configured frontend url (self-hosted or custom pureml frontend instance)
        frontend_url = (
            puremlconfig.data["frontend_url"]
            if "frontend_url" in puremlconfig.data
            else "https://pureml.com/"
        )
    else:
        # default frontend url (production cloud frontend)
        frontend_url = "https://pureml.com/"
    return frontend_url


class BackendSchema(Singleton_BaseModel):

    BASE_URL: str = get_backend_base_url()
    FRONTEND_BASE_URL: str = get_frontend_base_url()
    INTEGRATIONS: dict = {
        "s3": {
            "name": "AWS S3 Object Storage",
            "secrets": [
                "access_key_id",
                "access_key_secret",
                "bucket_location",
                "bucket_name",
            ],
        },
        "r2": {
            "name": "Cloudflare R2 Object Storage",
            "secrets": [
                "access_key_id",
                "access_key_secret",
                "account_id",
                "bucket_name",
                "public_url",
            ],
        },
    }

    class Config:
        arbitrary_types_allowed = True

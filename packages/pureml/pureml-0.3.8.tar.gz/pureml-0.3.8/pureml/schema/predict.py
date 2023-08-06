from pydantic import BaseModel
from .paths import PathSchema
import os
from .types import DataTypes


class Input(BaseModel):
    type: DataTypes
    shape: tuple = None


class Output(BaseModel):
    type: DataTypes = None
    shape: tuple = None


class PredictSchema(BaseModel):
    paths: PathSchema = PathSchema().get_instance()

    PREDICT_NAME: str = "predict.py"
    REQUIREMENTS_NAME: str = "requirements.txt"
    RESOURCES_NAME: str = "resources.zip"

    PATH_PREDICT: str = os.path.join(paths.PATH_PREDICT_DIR, PREDICT_NAME)
    PATH_PREDICT_USER: str = os.path.join(os.getcwd(), PREDICT_NAME)

    PATH_PREDICT_REQUIREMENTS: str = os.path.join(
        paths.PATH_PREDICT_DIR, REQUIREMENTS_NAME
    )
    PATH_PREDICT_REQUIREMENTS_USER: str = os.path.join(os.getcwd(), REQUIREMENTS_NAME)

    PATH_RESOURCES: str = os.path.join(paths.PATH_PREDICT_DIR, RESOURCES_NAME)
    PATH_RESOURCES_DIR_DEFAULT: str = "./"  # os.getcwd()

    resource_format: str = "zip"
    dirs_to_ignore: list = [".pureml", ".venv", "__pycache__"]

    class Config:
        arbitrary_types_allowed = True

from pydantic import BaseModel, root_validator, validator
from .singleton import Singleton_BaseModel
import typing
import os


class PathSchema(Singleton_BaseModel):

    PATH_PUREML_RELATIVE = ".pureml"
    PATH_PREDICT_DIR_RELATIVE = "predict"

    PATH_USER_TOKEN = os.path.join(
        os.path.expanduser("~"), PATH_PUREML_RELATIVE, "token"
    )

    PATH_USER_PROJECT_DIR = os.path.join(os.getcwd(), PATH_PUREML_RELATIVE)

    PATH_USER_PROJECT = os.path.join(PATH_USER_PROJECT_DIR, "pure.project")

    PATH_CONFIG = os.path.join(PATH_USER_PROJECT_DIR, "config.pkl")  # 'temp.yaml'

    PATH_ARTIFACT_DIR = os.path.join(PATH_USER_PROJECT_DIR, "artifacts")
    PATH_ARRAY_DIR = os.path.join(PATH_USER_PROJECT_DIR, "array")
    PATH_AUDIO_DIR = os.path.join(PATH_USER_PROJECT_DIR, "audio")
    PATH_FIGURE_DIR = os.path.join(PATH_USER_PROJECT_DIR, "figure")
    PATH_TABULAR_DIR = os.path.join(PATH_USER_PROJECT_DIR, "tabular")
    PATH_VIDEO_DIR = os.path.join(PATH_USER_PROJECT_DIR, "video")
    PATH_IMAGE_DIR = os.path.join(PATH_USER_PROJECT_DIR, "image")

    PATH_DATASET_DIR = os.path.join(PATH_USER_PROJECT_DIR, "dataset")

    PATH_MODEL_DIR = os.path.join(PATH_USER_PROJECT_DIR, "model")

    PATH_PREDICT_DIR = os.path.join(PATH_USER_PROJECT_DIR, PATH_PREDICT_DIR_RELATIVE)

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=False)
    def create_base_folders(cls, values):
        os.makedirs(values["PATH_USER_PROJECT_DIR"], exist_ok=True)

        return values

    @root_validator(pre=False)
    def create_log_folders(cls, values):
        os.makedirs(values["PATH_ARTIFACT_DIR"], exist_ok=True)
        os.makedirs(values["PATH_ARRAY_DIR"], exist_ok=True)
        os.makedirs(values["PATH_AUDIO_DIR"], exist_ok=True)
        os.makedirs(values["PATH_FIGURE_DIR"], exist_ok=True)
        os.makedirs(values["PATH_TABULAR_DIR"], exist_ok=True)
        os.makedirs(values["PATH_VIDEO_DIR"], exist_ok=True)
        os.makedirs(values["PATH_IMAGE_DIR"], exist_ok=True)

        return values

    @root_validator(pre=False)
    def create_model_folders(cls, values):
        os.makedirs(values["PATH_MODEL_DIR"], exist_ok=True)

        return values

    @root_validator(pre=False)
    def create_dataset_folders(cls, values):
        os.makedirs(values["PATH_DATASET_DIR"], exist_ok=True)

        return values

    @root_validator(pre=False)
    def create_predict_folders(cls, values):
        os.makedirs(values["PATH_PREDICT_DIR"], exist_ok=True)

        return values

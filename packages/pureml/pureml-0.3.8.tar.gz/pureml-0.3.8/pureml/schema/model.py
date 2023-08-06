from pydantic import BaseModel
from .paths import PathSchema
from .backend import BackendSchema
import os


class ModelSchema(BaseModel):
    paths: PathSchema = PathSchema().get_instance()
    backend: BackendSchema = BackendSchema().get_instance()

    PATH_MODEL_README: str = os.path.join(paths.PATH_MODEL_DIR, "ReadME.md")
    PATH_MODEL: str = os.path.join(paths.PATH_MODEL_DIR, "ran.pkl")

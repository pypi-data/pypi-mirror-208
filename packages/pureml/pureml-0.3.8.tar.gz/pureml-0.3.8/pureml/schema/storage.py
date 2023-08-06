from pydantic import BaseModel, root_validator

from pureml.schema.singleton import Singleton_BaseModel


class StorageSchema(Singleton_BaseModel):

    STORAGE: str = "PUREML-STORAGE"

    class Config:
        arbitrary_types_allowed = True

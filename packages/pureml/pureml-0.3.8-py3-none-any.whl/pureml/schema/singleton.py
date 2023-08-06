from pydantic import BaseModel


class Singleton_BaseModel(BaseModel):
    _instance = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.__class__._instance:
            self.__class__._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

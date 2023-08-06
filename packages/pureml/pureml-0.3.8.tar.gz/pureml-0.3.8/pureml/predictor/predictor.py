from pydantic import BaseModel, Field
import typing
from typing import List, Any
from abc import ABC, abstractmethod
from pureml.schema import Input, Output
from enum import Enum


class BasePredictor(BaseModel, ABC):
    label: str
    model: Any = None
    input: Input
    output: Output = Output()
    requirements_py: list = None
    requirements_sys: list = None

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def load_models(self):
        pass

    @abstractmethod
    def predict(self, **kwargs: typing.Any):
        pass

    # @abstractmethod
    def load_requirements_py(self):
        pass

    # @abstractmethod
    def load_requirements_sys(self):
        pass

    # @abstractmethod
    def load_resources(self):
        pass

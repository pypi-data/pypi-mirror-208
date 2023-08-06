from .classification import Classification
from .regression import Regression
from pydantic import BaseModel, root_validator
import typing
from typing import Literal
from enum import Enum


class TaskTypes(str, Enum):
    classification = "classification"
    regression = "regression"


class Grader(BaseModel):
    # def __init__(self, task_type):
    task_type: TaskTypes

    kwargs: typing.Any = None
    scores: dict = {}
    task_grader: typing.Any = None

    # print(self.task_grader)

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def _set_fields(cls, values: dict) -> dict:

        task_type = values["task_type"]

        if task_type is not None:

            if task_type == TaskTypes.classification:
                task_grader = Classification()
            elif task_type == TaskTypes.regression:
                task_grader = Regression()
            else:
                task_grader = None

            values["task_grader"] = task_grader

        return values

    def compute(self, references, predictions, prediction_scores=None, **kwargs):

        # print(self.task_grader)
        if self.task_grader is not None:
            # print('task grader is not none')
            self.task_grader.kwargs = kwargs
            self.task_grader.references = references
            self.task_grader.predictions = predictions
            self.task_grader.prediction_scores = prediction_scores

            self.scores = self.task_grader.compute()

        return self.scores


def grader(task_type, **kwargs):
    grade = Grader(task_type=task_type)

    return grade

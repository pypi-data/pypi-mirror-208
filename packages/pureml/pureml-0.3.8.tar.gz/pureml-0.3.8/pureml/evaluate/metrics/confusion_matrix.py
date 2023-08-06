from sklearn.metrics import confusion_matrix
import numpy as np


class ConfusionMatrix:
    def __init__(self):
        self.name = "confusion_matrix"
        self.input_type = "int"
        self.output_type = None
        self.kwargs = None

    def parse_data(self, data):

        return data

    def compute(
        self, references, predictions, normalize=None, sample_weight=None, **kwargs
    ):

        matrix = confusion_matrix(
            y_true=references,
            y_pred=predictions,
            normalize=normalize,
            sample_weight=sample_weight,
        )

        matrix = {self.name: np.array(matrix, dtype=float)}

        return matrix

from .metrics import Accuracy, Precision, Recall, F1, ConfusionMatrix


class Classification:
    def __init__(self):
        self.task_type = "classification"

        self.kwargs = None

        self.references = None
        self.predictions = None
        self.prediction_scores = None

        self.label_type = "binary"

        self.metrics = [
            Accuracy(),
            Precision(),
            Recall(),
            F1(),
            ConfusionMatrix(),
        ]  # , ROC_AUC()]
        self.scores = {}

    def compute(self):
        self.setup()

        for m in self.metrics:
            # Adding  prediction scores to kwargs. It will be utilized my metrics needing it(roc_auc).
            self.kwargs["prediction_scores"] = self.prediction_scores

            score = m.compute(
                references=self.references, predictions=self.predictions, **self.kwargs
            )

            self.scores.update(score)

        return self.scores

    def setup(self):
        self.is_multiclass()
        self.setup_kwargs()

    def get_predictions(self):
        pass

    def is_multiclass(self):
        if self.predictions is not None:
            labels_all = set(self.references).union(self.predictions)
            if len(labels_all) > 2:
                self.label_type = "multilabel"

    def setup_kwargs(self):
        if "average" not in self.kwargs:
            if self.label_type == "multilabel":
                self.kwargs["average"] = "micro"

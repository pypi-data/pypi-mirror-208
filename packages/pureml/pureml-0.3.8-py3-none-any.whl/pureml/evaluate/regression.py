from .metrics import MAE, MSE


class Regression():
    def __init__(self):
        self.task_type = 'regression'

        self.kwargs = None
        self.evaluator = None
        self.metrics = [MSE(), MAE()]

        self.scores = {}
    

    def compute(self):
        
        for m in self.metrics:
            #Adding  prediction scores to kwargs. It will be utilized my metrics needing it(roc_auc).
            self.kwargs['prediction_scores'] = self.prediction_scores

            score = m.compute(references=self.references, predictions=self.predictions, **self.kwargs)

            self.scores.update(score)

        return self.scores

    

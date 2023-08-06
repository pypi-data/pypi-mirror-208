from sklearn.metrics import roc_auc_score


class ROC_AUC():

    def __init__(self):
        self.name = 'roc_auc'
        self.input_type = 'float'
        self.output_type = None
        self.kwargs = None
        

    def parse_data(self, data):
        
        return data



    def compute(self, references, predictions=None, prediction_scores=None, average="macro", sample_weight=None,
                max_fpr=None, multi_class="raise", labels=None, **kwargs):
        
        if prediction_scores is None and predictions is None:
            score = None
        elif predictions is None:
            score = roc_auc_score(y_true=references, y_score=prediction_scores, average=average, sample_weight=sample_weight,
                                multi_class=multi_class, max_fpr=max_fpr, labels=labels)
            score = float(score)
        elif prediction_scores is None:
            score = roc_auc_score(y_true=references, y_score=predictions, average=average, sample_weight=sample_weight,
                                multi_class=multi_class, max_fpr=max_fpr, labels=labels)
            score = float(score)
        
        score = {
            self.name : score
            }
 

        return score
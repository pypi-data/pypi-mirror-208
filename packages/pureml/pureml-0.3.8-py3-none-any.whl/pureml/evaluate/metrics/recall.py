
from sklearn.metrics import recall_score


class Recall():

    def __init__(self):
        self.name = 'recall'
        self.input_type = 'int'
        self.output_type = None
        self.kwargs = None
        

    def parse_data(self, data):
        
        return data



    def compute(self, predictions, references, labels=None, pos_label=1, average="binary", 
                sample_weight=None, zero_division="warn", **kwargs):
        
        score = recall_score(y_true=references, y_pred=predictions, labels=labels, pos_label=pos_label, 
                             average=average, sample_weight=sample_weight, zero_division=zero_division)
        
        score = {
            self.name : float(score) if score.size == 1 else score
            }

        return score
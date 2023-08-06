
from sklearn.metrics import accuracy_score


class Accuracy():

    def __init__(self):
        self.name = 'accuracy'
        self.input_type = 'int'
        self.output_type = None
        self.kwargs = None
        

    def parse_data(self, data):
        
        return data



    def compute(self, references, predictions, normalize=True, sample_weight=None, **kwargs):

        score = accuracy_score(y_true=references, y_pred=predictions, normalize=normalize,
                                sample_weight=sample_weight)
        
        score = {
            self.name : float(score)
            }
 

        return score
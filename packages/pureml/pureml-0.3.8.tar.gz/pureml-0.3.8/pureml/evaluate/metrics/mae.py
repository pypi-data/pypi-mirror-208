from sklearn.metrics import mean_absolute_error


class MAE():

    def __init__(self):
        self.name = 'mae'
        self.input_type = 'float'
        self.output_type = None
        self.kwargs = None
        

    def parse_data(self, data):
        
        return data



    def compute(self, predictions, references, sample_weight=None, multioutput="uniform_average", **kwargs):
        
        score = mean_absolute_error(y_true=references, y_pred=predictions, sample_weight=sample_weight, multioutput=multioutput)
        
        score = {
            self.name : float(score)
            }
 

        return score
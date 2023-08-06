from sklearn.metrics import mean_squared_error


class MSE():

    def __init__(self):
        self.name = 'mse'
        self.input_type = 'float'
        self.output_type = None
        self.kwargs = None
        

    def parse_data(self, data):
        
        return data



    def compute(self, predictions, references, sample_weight=None, multioutput="uniform_average", squared=True, **kwargs):

        score = mean_squared_error(y_true=references, y_pred=predictions, sample_weight=sample_weight,
                                    multioutput=multioutput, squared=squared)
        
        score = {
            self.name : float(score)
            }
 

        return score
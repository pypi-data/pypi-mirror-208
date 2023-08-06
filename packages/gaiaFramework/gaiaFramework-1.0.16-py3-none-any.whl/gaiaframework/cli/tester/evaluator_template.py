
from gaiaframework.base.tester.evaluator_logic import DS_Evaluator


class generatedClass(DS_Evaluator):
    def __init__(self):
        super().__init__()

    def get_confusion_matrix(self, true_label, prediction):
        """
        Model evaluation function, to be implemented per project in evaluator.py file
        """
        raise NotImplementedError

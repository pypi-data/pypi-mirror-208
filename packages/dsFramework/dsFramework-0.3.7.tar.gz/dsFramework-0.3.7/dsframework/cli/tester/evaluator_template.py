
from dsframework.base.tester.evaluator_logic import ZIDS_Evaluator


class generatedClass(ZIDS_Evaluator):
    def __init__(self):
        """! generatedClass initializer """
        ##
        # @hidecallgraph @hidecallergraph
        super().__init__()

    def get_confusion_matrix(self, true_label, prediction, index):
        """! Model evaluation function, to be implemented per project in evaluator.py file

        Important:
            This method is not implemented, please override to use its functionality.
        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    def prepare_row_result(self, ground_truth, model_predication, conf_mat):
        """! Preparation for each row before calling each attribute get_confusion_matrix func

        Args:
            ground_truth:str : DataSet ground truth string
            model_predication:str : Model predication string
            conf_mat:dict : Confusion matrix for one row on the DataSet
        Important:
            This method is not implemented, please override to use its functionality.
        Raises:
            NotImplementedError
        """
        raise NotImplementedError

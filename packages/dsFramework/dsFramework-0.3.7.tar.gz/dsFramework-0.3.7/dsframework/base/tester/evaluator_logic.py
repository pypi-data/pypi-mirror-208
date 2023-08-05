from pandas import DataFrame
from pydantic import BaseModel
from dsframework.base.common.regex_handler import RegexHandler
from typing import Optional
import numpy

##
# @file
# @brief Includes Evaluator base class for local and cloud evaluation, ConfusionMatrix class and ConfusionRow to hold
# evaluation result.

class ZIDS_Evaluator():
    """ZIDS_Evaluator base class for evaluator.py, it is used in local and cloud evaluation."""
    def __init__(self):
        """ZIDS_Evaluator initializer"""
        pass


    def string_normalize(self, s:str) -> Optional[str]:
        """! String normalize currently we are doing those steps:
            1. Removing leading and trailing whitespaces (.strip() )
            2. Removing punctuations (RegexHandler.remove_punc)
            3. Change the string to lowercases (.lower() )
        @verbatim
        Args:
           s : input string
        Returns:
           s : normalized string
        @endverbatim
        """
        if (s is None) or (s != s):  # handle empty input : s != s --> check whether it's NAN
            return s
        s = s.strip()
        s = RegexHandler.remove_punct(s)
        s = s.lower()
        return s

    @staticmethod
    def partial_match(part_str, full_str):
        """! Partial match method

        Args:
            part_str:str :Candidate string to be searched in the full string
            full_str:str :Searchable, full string
        Returns:
            bool: There was a partial match
        """
        if part_str in full_str and (len(part_str) / len(full_str) > 0.2):
            return True
        return False

    @staticmethod
    def levenshtein_distance(token1, token2):
        """! Levenshtein distance calculation

        Args:
            token1:string : first string
            token2:string : second string
        Returns:
            int: Levenshtein distance
        """
        distances = numpy.zeros((len(token1) + 1, len(token2) + 1))
        for t1 in range(len(token1) + 1):
            distances[t1][0] = t1
        for t2 in range(len(token2) + 1):
            distances[0][t2] = t2
        a = 0
        b = 0
        c = 0
        for t1 in range(1, len(token1) + 1):
            for t2 in range(1, len(token2) + 1):
                if (token1[t1 - 1] == token2[t2 - 1]):
                    distances[t1][t2] = distances[t1 - 1][t2 - 1]
                else:
                    a = distances[t1][t2 - 1]
                    b = distances[t1 - 1][t2]
                    c = distances[t1 - 1][t2 - 1]
                    if (a <= b and a <= c):
                        distances[t1][t2] = a + 1
                    elif (b <= a and b <= c):
                        distances[t1][t2] = b + 1
                    else:
                        distances[t1][t2] = c + 1
        #self.print_distances(distances, len(token1), len(token2))
        return distances[len(token1)][len(token2)]

    def print_distances(self, distances, token1Length, token2Length):
        """! Print 2 dimensional matrix (distance between 2 tokens) - only for debug"""
        for t1 in range(token1Length + 1):
            for t2 in range(token2Length + 1):
                print(int(distances[t1][t2]), end=" ")
            print()

    def evaluate_model_predictions(self, df_from_model: DataFrame) -> DataFrame:
        """! Apply evaluation function (_get_confusion_matrix) on every incoming Dataframe row.

        Args:
            df_from_model: A dataframe containing both labeled data and model predictions
        Returns:
            Altered dataframe with a new column 'confusion_matrix' that holds a list of 'ConfusionRow' objects
        """
        conf_mat = []
        df_from_model['confusion_matrix'] = df_from_model.apply(lambda row:
                                                                self.prepare_row_result(row.pred, row.pred_model, conf_mat),
                                                                axis=1)

        return df_from_model

    def get_confusion_matrix(self, true_label, prediction, field_name):
        """! Model evaluation function, to be implemented per project in evaluator.py file"""
        raise NotImplementedError

    def prepare_row_result(self, grand_truth, model_predication, cm):
        """! Preparation for each row before calling each attribute get_confusion_matrix func"""
        raise NotImplementedError

    # @staticmethod
    def get_confusion_matrix_abs_string(self, true_label, prediction, field_name):
        """! Calculate confusion matrix string vs string

        Args:
            true_label: string : ground truth (from DataSet)
            prediction: string : model prediction
            field_name: string : field/attribute name
        Returns:
            {f'{field_name}': confusion_matrix}
        """

        #TODO  Add configure values: per Attrubuite (for example job_title-> cm calc with ExactMatch/LevenshteinDist/PartialMatch)
        confusion_matrix = {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
        dist = self.levenshtein_distance(true_label, prediction)
        threshold = 2.1
        if (dist < threshold) and prediction:
            confusion_matrix['tp'] += 1
        elif (dist > threshold) and (not prediction):  # true_label != prediction
            confusion_matrix['fn'] += 1
        elif (dist < threshold) and (not prediction):  # true_label == prediction == empty
            confusion_matrix['tn'] += 1
        elif (dist > threshold) and prediction and true_label:
            confusion_matrix['fn'] += 1
            confusion_matrix['fp'] += 1
        elif (not true_label) and prediction:  # true_label == 0 and prediction == 1 OR (true_label valid but far from prediction)
            confusion_matrix['fp'] += 1
        else:
            print('ERROR - should not enter this case - sanity check|', true_label, prediction)
        return {f'{field_name}': confusion_matrix}

    @staticmethod
    def get_confusion_matrix_binary(true_label, prediction, field_name=None):
        """! Gets a single confusion matrix, in a form of a dictionary:
        @code {.py}
        confusion_matrix = {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
        @endcode
        """
        confusion_matrix = {'tp': 0, 'fp': 0, 'fn': 0, 'tn': 0}
        if true_label == 1 and prediction == 1:
            confusion_matrix['tp'] = 1
        elif true_label == 1 and prediction == 0:
            confusion_matrix['fn'] = 1
        elif true_label == 0 and prediction == 0:
            confusion_matrix['tn'] = 1
        else:  # true_label == 0 and prediction == 1
            confusion_matrix['fp'] = 1
        if field_name:
            return {f'{field_name}': confusion_matrix}
        else:
            return {'cm': confusion_matrix}


class ConfusionMatrix(BaseModel):
    """Confusion matrix class, used as a base class for ConfusionRow, holds the evaluation results and
    provides methods to calculate required matrix parameters, such as precision, recall and f1."""
    def __init__(self):
        self.tp: int = 0  # True Positive
        self.tn: int = 0  # True Negative
        self.fp: int = 0  # False Positive
        self.fn: int = 0  # False Negative

        self.precision: float = 0
        self.f1: float = 0
        self.recall: float = 0

    def __add__(self, other):
        """Add results to confusion matrix"""
        _sum = ConfusionMatrix(
            tp=self.tp + other.tp,
            fp=self.fp + other.fp,
            fn=self.fn + other.fn,
            tn=self.tn + other.tn,
        )
        _sum.calc()
        return _sum

    def precision_calc(self):
        """Calculate precision parameter: true_positive / (true_positive + false_positive) """
        sum_ = self.tp + self.fp
        if sum_:
            return self.tp / sum_
        else:
            return 0

    def recall_calc(self):
        """Calculate recall parameter: true_positive / (true_positive + false_negative) """
        sum_ = self.tp + self.fn
        if sum_:
            return self.tp / sum_
        else:
            return 0

    def f1_calc(self):
        """Calculate f1 parameter: 2 * (precision * recall) / (precision + recall) """
        precision_ = self.precision
        recall_ = self.recall
        if precision_ + recall_ > 0:
            return 2 * (precision_ * recall_) / (precision_ + recall_)
        return 0

    def calc(self):
        """Calls precision, recall and f1 parameters calculations."""

        ## Precision parameter value
        self.precision= round(self.precision_calc(),3)
        ## Recall parameter value
        self.recall = round(self.recall_calc(), 3)
        ## f1 parameter value
        self.f1 = round(self.f1_calc(), 3)


class ConfusionRow(ConfusionMatrix):
    """! This class holds information regarding evaluation result of a single attribute that was sent for evaluation.
    It inherits from the ConfusionMatrix class to enable confusion matrix abilities, and will eventually output
    all relevant values for a single attribute. The evaluator output should be a list of objects from this class type
    """

    def __init__(self, name: str = "generic_cm"):
        """! ConfusionRow initializer."""

        ##
        # @hidecallgraph @hidecallergraph

        super().__init__()
        ## Assigns a name, defaults name: str = "generic_cm"
        self.name = name
        self.pred_val: list = []
        self.target_val: list = []

    def set_val_str(self, target: [str, None], pred: [str, None]):
        """! Evaluates a string value and updates confusion matrix.

        Args:
            target: Ground truth
            pred: Current prediction.

        Raises:
            ValueError: On wrong input values.
        """
        # pred='' and target=''
        if pred in [None, ''] and target in [None, '']:
            self.tn += 1
        # pred='' and target='sdfsdf'
        elif pred in [None, ''] and target not in [None, '']:
            self.fn += 1
        # ('a'!='b') or (pred='sdfsdf' & target ='')
        elif pred != target:
            self.fp += 1
        elif pred == target:
            self.tp += 1

        else:
            raise ValueError

        self.pred_val.append(pred)
        self.target_val.append(target)
        self.calc()

    def set_val_int(self, target: int, pred: int, zero_is_empty=False):
        """! Evaluates an integer value and updates confusion matrix.

        Args:
            target: Ground truth
            pred: Current prediction.
            zero_is_empty: Default false - adds values to pred_val and target_val.

        """
        if pred == target:
            if (pred != 0) or (zero_is_empty is False):
                self.tp += 1
        elif pred > target:
            self.fp += 1
        elif target > pred:
            self.fn += 1

        if (zero_is_empty is False) or (pred != 0 or target != 0):
            self.pred_val.append(pred)
            self.target_val.append(target)
        self.calc()

    def set_val_list_count(self, target: [int, None], pred: [int, None]):
        """! Evaluates an integer value and updates confusion matrix.

        Args:
            target: Ground truth
            pred: Current prediction.

        """
        if pred is None and target is not None:
            self.fn += 1
        elif pred is not None and target is None:
            self.fp += 1
        elif pred == target:
            self.tp += target
        elif pred > target:
            self.fp += 1
        elif target > pred:
            self.fn += 1

        self.pred_val.append(pred)
        self.target_val.append(target)
        self.calc()

    def set_val_check_list_of_list(self, col: list, exp: list, pre_comp_func_l=[]):
        """! Compare two list and count how many values UNIQUE from each appears at the other.

        Args:
            col: List 1
            exp: List 2
            pre_comp_func_l: Not used
        """
        ##
        # examples:
        # @code{.py}
        # miss col - Exp: [A, B, C] Col: [B,C] tp:2 fn:1
        # miss exp - Exp: [A] Col: [A, B, C] tp:1 fp: 2
        # @endcode
        # The Q unique or not unique:
        # @code{.py}
        # unique     - Exp: [A,A,A] col [A,B,B] tp:1 fp:1
        # unique     - Exp: [A,A,A,A] col [A,B,B] tp:1 fp:1
        # @endcode
        # or
        # @code{.py}
        # not unique - Exp: [A,A,A] col [A, B] tp:1 fp: 1 fn: 1
        # not unique - Exp: [A,A,A,A] col [A,B] tp:1 fp:1 fn :2
        # tmp_pred = copy.deepcopy(pred)
        # tmp_target = copy.deepcopy(target)
        #
        # for func in pre_comp_func_l:
        #     tmp_pred = func(record_l=tmp_pred)
        #     tmp_target = func(record_l=tmp_target)
        # @endcode

        tmp_col = col
        tmp_exp = exp

        exp_idx = 0
        for exp_idx, exp in enumerate(tmp_exp):
            if exp_idx < len(tmp_col):
                if exp == tmp_col[exp_idx]:
                    self.tp += 1
                else:
                    # found values on pred and target that mismatch
                    self.fp += 1
            else:
                # no value at predict
                self.fn += 1

        if exp_idx + 1 < len(tmp_col):
            # adiel: tn used to mark error in this case YAK!
            self.fp += len(tmp_col) - (exp_idx + 1)
        self.calc()

    def set_exp_col_cm(self, match_num, exp_miss, col_miss):
        """! Set results to self confusion matrix.

        Args:
            match_num: Sets true_positive
            exp_miss: Sets false negative
            col_miss: Sets false positive.

        """

        # row.set_exp_col_cm(match_num=len(order_l['match_exp']), exp_miss=len(order_l['exp_no']), col_miss=len(order_l['col_no']))
        ## True positive
        self.tp = match_num
        ## False negative
        self.fn = exp_miss
        ## False positive
        self.fp = col_miss
        self.calc()

    def get_cols_per_attr(attr):
        """! Gets a list of attribute strings per confusion matrix value.

        Returns:
            [f'{attr}_pred', f'{attr}_target', f'{attr}_prob', f'{attr}_tp', f'{attr}_fp', f'{attr}_tn', f'{attr}_fn']
        """
        return [f'{attr}_pred', f'{attr}_target', f'{attr}_prob', f'{attr}_tp', f'{attr}_fp', f'{attr}_tn',
                f'{attr}_fn']

    def get_server_tester(self):
        """! Constructs a dictionary with confusion matrix, pred, prob and target results.

        Returns:
            Dictionary with results.
        """
        self.calc()
        result = {
            self.name + '_fn': self.fn,
            self.name + '_fp': self.fp,
            self.name + '_tn': self.tn,
            self.name + '_tp': self.tp,
            self.name + '_pred': str(self.pred_val),
            self.name + '_prob': -1,
            self.name + '_target': str(self.target_val),
        }
        return result

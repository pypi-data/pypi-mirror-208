from dsframework.base.trainer.comparison import ZIDSTrainerComparison

##
# @file
# @brief generatedClass class, executes metrics results comparison for two models.


class generatedClass(ZIDSTrainerComparison):
    """ Comparison class, is where we compare two model test metric results.

    Basic comparison is supplied in base class of the compare() method. Override compare as required.
    Metrics evaluated are defined in config.py -> metrics section.
    """
    comparison_results = {}

    def __init__(self, test_results, eval_results, metrics_config):
        super().__init__(test_results, eval_results, metrics_config)

    def compare(self):
        """! Implement you comparison between your model and the evaluated model.
        Basic comparison is supplied in base class of the compare() method.

        For example:
            @code
            if self.test_results is None or self.eval_results is None:
                return "No test results found."

            self.comparison_results = {
                metric: {'trained': self.test_results[metric], 'eval': self.eval_results[metric]}
                for metric in self.metrics
                if metric in self.test_results and metric in self.eval_results and self.metrics[metric]}

            return self.comparison_results
            @endcode
        """

        if not self.comparison_results:
            raise "Compare not implemented. Please implement in comparison.py -> compare()"

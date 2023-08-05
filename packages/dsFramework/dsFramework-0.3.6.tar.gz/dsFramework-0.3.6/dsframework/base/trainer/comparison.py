class ZIDSTrainerComparison:

    comparison_results = {}

    test_results = None
    eval_results = None
    metrics = None  # ['precision', 'accuracy', 'recall', 'f1', 'confusion_matrix']

    def __init__(self, test_results, eval_results, metrics_config):

        self.test_results = test_results
        self.eval_results = eval_results
        self.metrics = metrics_config

    def compare(self):
        if self.test_results is None or self.eval_results is None:
            return "No test results found."

        self.comparison_results = {
            metric: {'trained': self.test_results[metric], 'prd': self.eval_results[metric]}
            for metric in self.metrics
            if metric in self.test_results and metric in self.eval_results and self.metrics[metric]}

        return self.comparison_results
    
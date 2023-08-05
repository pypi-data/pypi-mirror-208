from dsframework.base.trainer.test import ZIDSTrainerTest
from trainer.pl_wrapper.plmodel import generatedProjectNamePlmodel
from trainer.data import generatedProjectNameData
from dsframework.base.trainer.pl_wrapper import *

##
# @file
# @brief generatedClass class, executes test process.


class generatedClass(ZIDSTrainerTest):
    """! Test class, runs the model against a labeled test dataset to evaluate its metrics.

        Three things needs to be done for this to work:
            1. Receive data_module with labeled dataset loaded.
            2. Load model
            3. Create and Run trainer instance.
    """

    def __init__(self, model_path=None, test_dataset_path=None, trainer_config=None, model_config=None, metrics_config=None,
                 save_path=''):
        """generatedClass Initializer.

        Runs trainer_setup() and load_model() methods/
        """

        self.data_class_test = None
        self.model_config = model_config
        self.metrics_config = metrics_config
        self.save_path = save_path

        super().__init__(model_path, test_dataset_path, trainer_config)

    def load_model(self, model_path):
        """! Loads a model

        Needs to be implemented.

        Example (pytorch lightning):
            self.model = generatedProjectNamePlmodel.load_from_checkpoint(
                model_path,
                model_config=self.model_config,
                metrics_config=self.metrics_config,
                trainer_config=self.trainer_config,
                save_path=self.save_path
            )
        """

        if self.model is None:
            raise Exception('load_model() method in test.py, not implement.')

    def create_data_module(self, tokenizer, test_dataset_path):
        """! Create the data module to use with the test process.


        Example:
            self.data_class_test = generatedProjectNameData(
                model_config=self.model_config,
                load_datasets=True,
                test_dataset_path=self.test_dataset_path,
                tokenizer=self.model.tokenizer)
        """
        if self.data_class_test is None:
            raise Exception('create_data_module() method in test.py, not implement.')

    def trainer_setup(self, trainer_config):
        """! Instantiate trainer class

        Needs to be implemented.

        Example (pytorch lightning):
            self.trainer = pl.Trainer(**trainer_config)
        """

        if self.trainer is None:
            raise Exception('trainer_setup() method in test.py, not implement.')

    def execute_test(self):
        """! Implement test process and return the results.

        Returns:
            test results - Metric results from test.

        Example (pytorch lightning):
            if self.model is None or self.data_class_test is None or self.trainer is None:
                return None
            self.trainer.test(self.model, self.data_class_test.get_data_module())

            return self.model.get_test_results()
        """

        raise Exception('Methods execute_test() not implemented in test.py.')

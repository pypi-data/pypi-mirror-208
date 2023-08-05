from trainer.pl_wrapper.data_module import generatedProjectNameDataModule
from dsframework.base.trainer.pl_wrapper import *
from dsframework.base.trainer.data import ZIDSTrainerData

##
# @file
# @brief generatedClass class, Datasets and functionality related to datasets.


class generatedClass(ZIDSTrainerData):
    """generatedClass, holds datasets and functionality related to it."""
    dataset_train = None
    dataset_validation = None
    dataset_test = None
    data_module = None

    def __init__(self, model_config=None, load_datasets=False, training_path=None, validation_path=None,
                 test_dataset_path=None, tokenizer=None):
        """generatedClass class initializer."""

        super().__init__(model_config, load_datasets, training_path, validation_path, test_dataset_path, tokenizer)

    def create_data_module(self):
        """! Creates data module in the format you use in the fit/train method. Called from super().__init__().

        Needs to be implemented.

        Example (pytorch lightning):
            self.data_module = generatedProjectNameDataModule(
                model_config=self.model_config,
                train_set=self.dataset_train,
                val_set=self.dataset_validation,
                test_set=self.dataset_test
            )

            return self.data_module
        """
        if self.data_module is None:
            raise Exception('Implement data module in data.py -> create_data_module()')

    def get_data_module(self):
        """! Returns data module in the format you use in the fit/train method.

        Returns:
            data_module

        """
        if self.data_module is None:
            raise Exception('Implement data module in data.py -> create_data_module()')

        return self.data_module

    def load_datasets(self, ds_training_path=None, ds_val_path=None, ds_test_path=None):
        """! Dataset loading.

        Args:
            ds_training_path: Path to training datasets
            ds_val_path: Path to validation datasets
            ds_test_path: Path to test datasets


        Example:
            @code
            if ds_training_path is None and ds_test_path is not None:
                ds_training_path = ds_test_path

            dataset = datasets.MNIST(ds_training_path, download=True, train=True,
                                     transform=transforms.ToTensor())
            self.dataset_train, self.dataset_validation = random_split(dataset, [55000, 5000])
            self.dataset_test = datasets.MNIST(ds_training_path, download=True, train=False,
                                               transform=transforms.ToTensor())

            if self.model_config['num_classes_conf_mat'] is None:
                try:
                    self.model_config['num_classes_conf_mat'] = len(self.dataset_train.dataset.classes)
                except Exception as e:
                    self.model_config['num_classes_conf_mat'] = None
                    print(f'Exception getting number of classes for confusion matrix, please set manually in config.py: {e}')
            @endcode
        """
        raise Exception('load_datasets() not implemented.')

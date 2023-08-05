class ZIDSTrainerData:

    dataset_train = None
    dataset_validation = None
    dataset_test = None
    data_module = None
    save_path = ''

    def __init__(self, model_config=None, load_datasets=False, training_path=None, validation_path=None,
                 test_dataset_path=None, tokenizer=None):
        self.model_config = model_config
        self.load_ds = load_datasets
        self.training_path = training_path
        self.validation_path = validation_path
        self.test_dataset_path = test_dataset_path
        self.tokenizer = tokenizer

        if self.load_ds:
            self.load_datasets(self.training_path, self.validation_path, self.test_dataset_path)

        self.create_data_module()

    def create_data_module(self):
        pass

    def get_data_module(self):

        self.data_module = None

        return self.data_module

    def load_datasets(self, ds_training_path=None, ds_val_path=None, ds_test_path=None):
        raise Exception('load_datasets() not implemented.')

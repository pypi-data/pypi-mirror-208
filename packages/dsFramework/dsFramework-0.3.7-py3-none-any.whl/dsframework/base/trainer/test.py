class ZIDSTrainerTest:

    trainer = None
    model = None
    data_module = None

    def __init__(self, model_path=None, test_dataset_path=None, trainer_config=None):
        self.model_path = model_path
        self.test_dataset_path = test_dataset_path
        self.trainer_config = trainer_config

        self.load_model(model_path)
        self.create_data_module(self.model.tokenizer, test_dataset_path)
        self.trainer_setup(self.trainer_config)

    def load_model(self, model_path):
        pass

    def create_data_module(self, tokenizer, test_dataset_path):
        pass

    def trainer_setup(self, trainer_config):
        pass

    def execute_test(self):
        pass

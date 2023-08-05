class ZIDSTrainClass:

    train_dataset = None
    validation_dataset = None
    trainer = None
    model = None
    data_module = None
    trainer_config = None
    model_config = None
    save_path = None

    def __init__(self, trainer_config=None, model_config=None, train_dataset=None, validation_dataset=None,
                 model=None, data_module=None, save_path=''):
        self.train_dataset = train_dataset
        self.validation_dataset = validation_dataset
        self.model = model
        self.data_module = data_module
        self.trainer_config = trainer_config
        self.model_config = model_config
        self.trainer = None  # trainer instance
        self.save_path = save_path

    def execute(self):
        """! Training process.

        for example:
            self.trainer = pl.Trainer(**self.config)
            self.trainer.fit(self.model, self.data_module)
            self.trainer.save_checkpoint("my_model.ckpt")
        """
        pass

    def get_trainer(self):
        return self.trainer

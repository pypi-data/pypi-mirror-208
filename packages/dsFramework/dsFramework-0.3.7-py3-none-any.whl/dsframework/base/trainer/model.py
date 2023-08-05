class ZIDSTrainerModel:
    
    def __init__(self, model_config, metrics_config, trainer_config, save_path):
                
        self.model = None
        self.model_config = model_config
        self.metrics_config = metrics_config
        self.trainer_config = trainer_config
        self.save_path = save_path
        
        self.define_model()

    def define_model(self):
        """! Implement model class in the format you use in the fit/train method.
        Create a new model or load from pretrained model.

        Needs to be implemented.

        Example (pytorch lightning):
            self.model = generatedProjectNamePlmodel(
                model_config=self.model_config,
                metrics_config=self.metrics_config,
                trainer_config=self.trainer_config,
                save_path=self.save_path
            )
        """
        if self.model is None:
            raise Exception('Implement model in model.py')

    def get_model(self):
        return self.model

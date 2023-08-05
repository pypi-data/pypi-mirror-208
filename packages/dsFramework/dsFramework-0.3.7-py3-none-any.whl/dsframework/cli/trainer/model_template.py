from dsframework.base.trainer.model import ZIDSTrainerModel
from trainer.pl_wrapper.plmodel import generatedProjectNamePlmodel

##
# @file
# @brief generatedClass class, defines model class.


class generatedClass(ZIDSTrainerModel):
    """Model class - defines the network, loss function etc."""

    def __init__(self, model_config, metrics_config, trainer_config, save_path):
        super().__init__(model_config, metrics_config, trainer_config, save_path)

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
        """Returns model class"""
        return self.model

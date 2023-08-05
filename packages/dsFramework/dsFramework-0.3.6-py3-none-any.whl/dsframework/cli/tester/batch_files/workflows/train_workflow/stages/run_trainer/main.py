"""! @brief Get Data stage, for obtaining data from a generic source, such as a database."""
import argparse
import os
import sys
from typing import Any
from json import loads as json_loads

from dsframework.base.batch.pipeline_stage_base import ZIDS_BatchPipelineStage
from trainer.main import Main
from trainer.config import config as trainer_config

##
# @file
# @brief Stage main class, implements ZIDS_Stage base class.
class RunTrainerStage(ZIDS_BatchPipelineStage):
    """! Stage class

    Implement a stage that will later be converted to an executable job in a specific workflow.
    """

    def __init__(self, stage_config):
        """! The Stage class (generatedStageName) initializer.
        Base class will load basic configuration parameters, additional fields should be added here

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
        """

        ##
        # @hidecallgraph @hidecallergraph
        print(f"Initializing Stage: {self.get_name()}")

        self.wf_name = "train"
        super().__init__(stage_config)

    def get_name(self):
        """! Get the stage name
        """
        return self.__class__.__name__

    def main(self, **kwargs: Any):
        """! Executes the main functionality of the stage.

            Args:
                **kwargs : Whatever is needed for the stage to run properly.
        """
        trainer_main_class = Main(cfg=trainer_config, training_path=os.getcwd() + '/datasets',
                          validation_path=os.getcwd() + '/datasets')
        trainer_main_class.execute_trainer(force_save_path='/trainer_tmp')
        trainer_main_class.copy_to_gs(self.bucket_name, self.folder_path, self.project_id)

        print('Trainer stage completed.')


if __name__ == "__main__":
    """! Executes the stage by instantiating it and calling the main function.
    Set up argument condition according to the usage of the written stage

        Args:
            System argument 1 - Configuration file
            System argument 2 - Start date
            System argument 3 - End date, received from Airflow
            System argument 4 - Placeholder for future parameters
    """

    parser = argparse.ArgumentParser(description='Configure and run RunTrainerStage class')
    parser.add_argument('config', type=str,
                        help='Configuration file')
    parser.add_argument('start_date', type=str, default='',
                        help='Start date, received from Airflow')
    parser.add_argument('end_date', type=str, default='',
                        help='End date, received from Airflow')
    parser.add_argument('params', nargs=argparse.REMAINDER,
                        help='Placeholder for future parameters')
    args = parser.parse_args()

    # Configure stage class and run
    stage = RunTrainerStage(json_loads(args.config))
    try:
        stage.update_stage_params(args.start_date, args.end_date, args.params)
        stage.main()
    except Exception as e:
        raise Exception(f" Stage failed with error: {e}")

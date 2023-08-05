"""! @brief Skeleton for implementing a specific stage to be used in a DataProc Workflow template."""

import logging
from json import loads as json_loads
from dsframework.base.batch.pipeline_stage_base import ZIDS_BatchPipelineStage
from dsframework.base.batch.pipeline_stage_base import parse_args

logger = logging.getLogger(__name__)


##
# @file
# @brief generatedStageName class, inherits ZIDS_BatchPipelineStage base class.
class generatedStageName(ZIDS_BatchPipelineStage):
    """! The stage class that will be later converted to an executable job in a specific workflow.
    See class ExampleStage for an example implementation of the load, run and finish methods.
    A method for initiating a SparkSession is available in the base class ZIDS_BatchPipelineStage
    For logging please use the module-level logger - 'logger'
    """

    def __init__(self, stage_config, start_date, end_date, params):
        """! The Stage class (generatedStageName) initializer.
        Base class will load basic configuration parameters, additional fields should be added here

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
                start_date: String, containing the starting date, received from Airflow
                end_date: String, containing the end date, received from Airflow
                params: List of a single Json string, containing extra parameters
        """
        self.wf_name = "generatedWFName"
        super().__init__(stage_config, start_date, end_date, params, logger)

    def load(self):
        """! The \'load\' phase is for loading input dataframes and running input data tests if needed
        """
        raise NotImplementedError

    def run(self):
        """! The \'run\' phase is for the transform logic
        """
        raise NotImplementedError

    def finish(self):
        """! The \'finish\' phase is for saving output dataframes and running output data tests if needed
        """
        raise NotImplementedError


if __name__ == "__main__":
    """! Executes the stage by parsing input arguments, instantiating the stage and 
         calling the __call__ function of the base class.
    """

    # Handle input arguments
    args = parse_args()

    # Configure stage class and run
    stage = generatedStageName(json_loads(args.config), args.start_date, args.end_date, args.params)
    try:
        stage()
    except Exception as e:
        raise Exception(f" Stage failed with error: {e}")




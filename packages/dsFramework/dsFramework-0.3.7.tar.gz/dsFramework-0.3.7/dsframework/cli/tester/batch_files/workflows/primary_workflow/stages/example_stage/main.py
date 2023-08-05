"""! @brief Get Data stage, for obtaining data from a generic source, such as a database."""

import sys
import logging
from json import loads as json_loads
from dsframework.base.batch.pipeline_stage_base import ZIDS_BatchPipelineStage
from dsframework.base.batch.pipeline_stage_base import parse_args

logger = logging.getLogger(__name__)


##
# @file
# @brief Stage main class, implements ZIDS_Stage base class.
class ExampleStage(ZIDS_BatchPipelineStage):
    """! Example Stage class
    Implement a stage that will later be converted to an executable job in a specific workflow.
    """

    def __init__(self, stage_config, start_date, end_date, params):
        """! The Stage class (ExampleStage) initializer.
        Base class will load basic configuration parameters, additional fields should be added here

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
        """

        ##
        # @hidecallgraph @hidecallergraph
        logger.info(f"Initializing Stage: {self.get_name()}")

        self.wf_name = "primary"
        self.highest_price_unit_df = None
        self.df = None

        super().__init__(stage_config, start_date, end_date, params, logger)

        self.spark = self.load_spark()
        logger.info(f"Stage {self.get_name()} Initialized")

    def get_name(self):
        """! Get the stage name
        """
        return self.__class__.__name__

    def load(self):
        """! The \'load\' phase is for loading input dataframes and running input data tests if needed
        """
        self.df = self.spark.read. \
            options(header='true', inferSchema='true').csv(f"gs://{self.bucket_name}/example_data/retail_day.csv")

    def run(self):
        """! The \'run\' phase is for the transform logic
        """
        self.df.printSchema()
        self.df.createOrReplaceTempView("sales")
        self.highest_price_unit_df = self.spark.sql("select * from sales where UnitPrice >= 3.0")

    def finish(self):
        """! The \'finish\' phase is for saving output dataframes and running output data tests if needed.
        This is also the place to close a spark session, if such was used.
        """
        self.highest_price_unit_df.write.mode("overwrite").parquet(f"{self.bucket_path}"
                                                                   f"/example_data/highest_prices_{self.project_id}.parquet")
        self.spark.stop()


if __name__ == "__main__":
    """! Executes the stage by instantiating it and calling the __call__ function of the base class.
    """

    # Handle input arguments
    args = parse_args()

    # Configure stage class and run
    stage = ExampleStage(json_loads(args.config), args.start_date, args.end_date, args.params)
    try:
        stage()
    except Exception as e:
        raise Exception(f" Stage failed with error: {e}")

"""! @brief ZIDS_Stage base class for the batch stage class."""
import argparse
import logging
import os
import time
from typing import Mapping, OrderedDict
from ujson import loads as json_loads
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame


##
# @file
# @brief Defines stage base class.
class ZIDS_BatchPipelineStage():
    def __init__(self, stage_config, start_date, end_date, params, logger):
        """! ZIDS_BatchPipelineStage initializer.
        Loads config file.

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
                start_date: String, containing the starting date, received from Airflow
                end_date: String, containing the end date, received from Airflow
                params: List of a single Json string, containing extra parameters
                logger: The logger instance that will be used throughout the stage
        """

        self.logger = logger
        logger.info(f"Initializing Stage: {self.get_name()} ")

        logger.info(f"{start_date = }, {end_date = }, {params = }")
        self.start_date = start_date
        self.end_date = end_date
        self.extra_params = json_loads(params[0])

        self.bucket_name = stage_config['bucket_name']
        self.project_id = stage_config['project_id']
        self.project_name = stage_config['project_name']
        self.region = stage_config['region']
        self.env_type = self.extra_params.get('ENV', 'development')

        user_email = ""
        if 'user_email' in stage_config:
            user_email = stage_config['user_email']

        self.unique_iteration_id = stage_config['unique_iteration_id']
        if self.unique_iteration_id:
            self.folder_path = os.path.join(self.project_name, user_email, self.wf_name,
                                            f"unique_iteration_id_{self.unique_iteration_id}")
        else:
            self.folder_path = os.path.join(self.project_name, user_email, self.wf_name, 'main')

        self.bucket_path = f"gs://{self.bucket_name}/{self.folder_path}"
        self.start_date = ""
        self.end_date = ""
        self.extra_params = ""

    def get_name(self):
        """! Get the stage name
            Returns:
                The stage name string
        """
        return self.__class__.__name__

    def load(self):
        # Override to load input dataframes, and run input data tests if needed
        raise NotImplementedError

    def run(self):
        # Override to execute transform
        raise NotImplementedError

    def finish(self):
        # Override to save output dataframes, and run output data tests if needed
        raise NotImplementedError

    def __call__(self):
        """Run load(), run(), and finish() and log the runtime"""
        start = time.time()

        stage_name = self.get_name()
        self.logger.info(f"Starting stage: {stage_name} ")
        self.load()
        self.logger.info(f"{stage_name}: Finished load()")
        self.run()
        self.logger.info(f"{stage_name}: Finished run()")
        self.finish()
        self.logger.info(f"{stage_name}: Finished finish()")
        elapsed = time.time() - start

        self.logger.info(f"Stage '{stage_name}' finished in " + '%0.1f min' % (elapsed / 60.0))

    def load_spark(self) -> SparkSession:  # TODO: Generalize this in order to receive config options.
        """! Basic loading of a spark session.

            Returns:
                A basic spark session
        """
        spark = SparkSession.builder \
            .appName(self.project_name + self.get_name()) \
            .config('spark.ui.showConsoleProgress', True) \
            .config("spark.sql.parquet.compression.codec", "gzip") \
            .config('spark.jars', 'gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar') \
            .getOrCreate()

        self.logger.info(f"Spark ID: {spark.sparkContext.applicationId}")
        return spark

    def send_df_to_bq(self, df: DataFrame, bq_dataset: str, bq_table: str, tmp_bucket: str):
        """! Sending a Spark dataframe to a bigquery table. Please override to change attributes
            Args:
                df: Spark dataframe to be written
                bq_dataset: BigQuery destination Dataset
                bq_table: BigQuery destination Table
                tmp_bucket: Temporary bucket, needed by the client
        """
        self.logger.info(f"Stage {self.get_name()}, write to bigquery (Dataset: {bq_dataset}, Table: {bq_table})")

        tmp_bucket_path = os.path.join(tmp_bucket, self.start_date)

        df.write \
            .format("bigquery") \
            .option("table", "{}.{}".format(bq_dataset, bq_table)) \
            .option("temporaryGcsBucket", tmp_bucket_path) \
            .option("allowFieldAddition", True) \
            .option("allowFieldRelaxation", True) \
            .mode('append') \
            .save()


class ZIDS_BatchPipeline:
    """! ZIDS_BatchPipelineStage initializer.
    Loads config file.

        Args:
            stage_config : Configuration dictionary, loaded from configuration file.

    """
    def __init__(self):
        # Override
        self.stages: Mapping[str, ZIDS_BatchPipelineStage] = {}
        self.logger = logging.getLogger(__name__)

    def run_stage(self, stage_name: str):
        if stage_name not in self.stages:
            stage_names = '\n'.join(sorted(self.stages.keys()))
            raise KeyError(f"Stage '{stage_name}' not found among stages:\n {stage_names}")

        stage = self.stages[stage_name]
        stage()

    def run_all_stages(self):

        assert type(self.stages) is OrderedDict, "Pipeline self.stages must be an OrderedDict to use run_all_stages()"

        if 'spark' in self.__dir__():
            try:
                # TODO -- not sure if this is needed, since all sparkConf parameters show up in the Spark Job page
                #   and it may be very long and verbose
                self.logger.info("Spark config:", self.spark.sparkContext.getConf().getAll())
            except:
                # self.spark wasn't a SparkSession object
                pass

        start = time.time()
        for stage_name, stage in self.stages.items():
            self.run_stage(stage_name)
        elapsed = time.time() - start

        self.logger.info('Finished all stages in %0.1f min' % (elapsed / 60.))


def parse_args():
    """! Basic function for parsing input arguments. If some of them change, feel free to override
    Args:
            System argument 1 - Configuration file
            System argument 2 - Start date, received from Airflow
            System argument 3 - End date, received from Airflow
            System argument 4 - Placeholder for future parameters
    """
    parser = argparse.ArgumentParser(description='Configure and run stage')
    parser.add_argument('config', type=str,
                        help='Configuration file')
    parser.add_argument('start_date', type=str, default='',
                        help='Start date, received from Airflow')
    parser.add_argument('end_date', type=str, default='',
                        help='End date, received from Airflow')
    parser.add_argument('params', nargs=argparse.REMAINDER,
                        help='Placeholder for future parameters')
    args = parser.parse_args()

    return args

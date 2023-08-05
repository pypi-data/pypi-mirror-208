import os
import sys
import argparse
from typing import List
from google.cloud.dataproc_v1.types.workflow_templates import TemplateParameter
from google.cloud.dataproc_v1.types import OrderedJob
from dsframework.base.batch.workflow_base import ZIDS_Workflow


class Workflow(ZIDS_Workflow):

    def __init__(self, workflow_name: str = ""):
        """! Loads config file and initializes parameters.
        """
        self.default_jars = ['gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar']
        main_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

        super().__init__(workflow_name)

        # Add general packages, as well as workflow specific ones, if available
        if not self.config["use_only_wf_packages"]:
            self.configure_pip_packages(main_project_path + '/requirements_docker.txt')

        curr_wf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"{self.wf_name}_workflow"))
        self.configure_pip_packages(curr_wf_path + f"/requirements_{self.wf_name}.txt", append=True)

        # Option for another build type - dependent on setup.py
        self.whl_file_name = f"{self.project_name}_{self.wf_name}.zip"

        # Initialize spark properties.
        self.spark_properties = self.config["spark_properties"]

    def create_job(self, stage_name, prerequisite_list=None) -> OrderedJob():
        """! Create a job from a given stage

            Args:
                stage_name: Name of the stage to create
                prerequisite_list: list of stage id's that are mandatory to run before current stage

            Returns:
                An Ordered Job, to be inserted into the workflow template
        """
        stage_dir = f'batch_files/stages/{stage_name}'
        python_files = [self.whl_file_name]
        archive_files = [self.whl_file_name]

        # Merge both basic configuration and stage specific ones
        if stage_name in self.spark_properties:
            stage_spark_properties = {**self.spark_properties['basic'], **self.spark_properties[stage_name]}
        else:
            stage_spark_properties = self.spark_properties['basic']

        # Convert to desired "List of lists" format
        spark_properties_list = [[key, value] for key, value in list(stage_spark_properties.items())]

        stage_job = self.create_ordered_job(stage_dir, spark_properties_list, python_files, archive_files)

        if prerequisite_list is not None:
            stage_job.prerequisite_step_ids = [f"{self.project_name}-{stage}" for stage in prerequisite_list]

        return stage_job

    def create_jobs(self) -> List[OrderedJob]:
        """! Generates a job for each of the workflow stages
            Returns:
                A List of OrderedJob, to be inserted into the workflow template
        """

        ordered_jobs = [self.create_job(stage['stage_name'], stage['prerequisites']) for stage in self.wf_stages]

        return ordered_jobs

    def finalize_jobs(self, workflow_template):
        """! Finalize the jobs, introduce additional parameters, etc.
            Args:
                workflow_template: Workflow templates. Includes jobs that we wish to modify
        """

        # Make sure to change jobs according to specific configuration
        if self.config['specific_jobs_to_run'] and len(self.config['specific_jobs_to_run']):
            specific_jobs_to_run = []
            for job in workflow_template.jobs:
                if job.step_id in self.config['specific_jobs_to_run']:
                    specific_jobs_to_run.append(job)
                    if self.config['force_remove_all_prerequisite']:
                        job.prerequisite_step_ids = []
                    if len(job.prerequisite_step_ids) and not all(
                            elem in specific_jobs_to_run for elem in job.prerequisite_step_ids):
                        raise Exception("job depends on another job not in specific_jobs_to_run list")
            workflow_template.jobs = specific_jobs_to_run

        # Set start and end dates from Airflow composer
        workflow_template.parameters = []

        start_date_param = TemplateParameter()
        start_date_param.description = "start date from airflow composer"
        start_date_param.name = "START_DATE"

        end_date_param = TemplateParameter()
        end_date_param.description = "end date from airflow composer"
        end_date_param.name = "END_DATE"

        extra_param = TemplateParameter()
        extra_param.description = "allow adding extra parameters"
        extra_param.name = "PARAMS"

        for job in workflow_template.jobs:
            start_date_param.fields.append("jobs['" + job.step_id + "'].pysparkJob.args[1]")
            end_date_param.fields.append("jobs['" + job.step_id + "'].pysparkJob.args[2]")
            extra_param.fields.append("jobs['" + job.step_id + "'].pysparkJob.args[3]")

        workflow_template.parameters.append(start_date_param)
        workflow_template.parameters.append(end_date_param)
        workflow_template.parameters.append(extra_param)

    def create_template_structure(self):
        """! Create the workflow template, and return it for external usage.
            Returns:
                workflow_template: A ready to use template, WorkflowTemplate() class
        """
        # Define template structure, along with cluster requirements
        workflow_template = self.build_template_structure()

        # Define jobs that this workflow will run on a given compute cluster
        workflow_template.jobs = self.create_jobs()

        # Finalize job parameters
        self.finalize_jobs(workflow_template)

        return workflow_template

    def create_workflow_template(self, create_yaml: bool = False):
        """! Create the workflow template, along with all relevant stages
            Args:
                create_yaml: Boolean, deciding whether we should create a yaml file out of the template
        """

        # Check if a cluster exists. If it does, we will work with it. If not, we'll use the managed cluster from the
        # configuration file
        self.check_cluster()

        # Define template structure
        workflow_template = self.create_template_structure()

        print(f'{workflow_template}')

        # Make sure that the template does not exist
        self.check_template()

        # If needed, create a .yaml file, don't use Cloud API
        if create_yaml:
            self.create_yaml_file(workflow_template)

        else:
            # Create template on Dataproc by using Cloud API
            self.create_template(workflow_template)


if __name__ == "__main__":
    """! Triggers the creation of the workflow template, starting from
    basic configuration, defining and creating jobs from the existing stages, 
    and up to creating and instantiating the workflow, if needed.
        Args:
        System argument 1 - Workflow name
        System argument 2 - Action to be performed on a template (create, delete, instantiate)
    """

    parser = argparse.ArgumentParser(description='Run various workflow related commands')
    parser.add_argument('--wf-name', type=str, default='primary',
                        help='workflow name which will be the base workflow for related actions')
    parser.add_argument('--action', type=str, default='create',
                        help='Workflow action (create / create_yaml / delete / instantiate')

    args = parser.parse_args()

    template_action = args.action

    workflow = Workflow(args.wf_name)

    if template_action == 'create':
        workflow.create_workflow_template()

    if template_action == 'create_yaml':
        workflow.create_workflow_template(create_yaml=True)

    # At this point, a template is either previously or recently created
    template = workflow.get_workflow_template()

    if template_action == 'delete' and template:
        workflow.delete_workflow_template(template)

    if template_action == 'instantiate' and template:
        workflow.instantiate_template(template)

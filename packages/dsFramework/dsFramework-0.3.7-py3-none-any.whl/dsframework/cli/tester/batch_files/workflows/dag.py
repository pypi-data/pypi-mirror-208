import sys
import argparse
from datetime import datetime, timedelta
from textwrap import dedent

from dsframework.base.batch.dag_base import ZIDS_Dag


class Dag(ZIDS_Dag):
    def __init__(self, workflow_name: str = ""):
        """! Loads config file and initializes parameters.
        Please make sure to determine the start date according to your project needs.
        """

        # dag params from airflow 1 - https://airflow.apache.org/docs/apache-airflow/1.10.3/macros.html
        # dag params from airflow 2 - https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html
        super().__init__(workflow_name)

        self.file_name = self.project_name + "_" + self.wf_name + "_dag.py"

        # This setting will give the dag an execution date of the day before its creation.
        self.dag_start_delay = 1

    def create_dag(self):
        """! Dag creation.
        This function creates the python file which contains the DAG itself.
        """

        with open(self.file_name, 'w') as dag_text_file:
            dag_text_file.write(dedent(self.get_basic_dag_code()))
        print(f"DAG file created: {self.file_name}")


if __name__ == "__main__":
    """! Triggers the creation of the workflow dag, which will instantiate a
    workflow template into an actual workflow, executing it.
    Through this module, we can create a dag file which contains instructions, regarding how to execute the 
    workflow template, and we can also import / remove it into / from an active GCP composer (Only for dev mode)
        Args:
            System argument 1 - Workflow to be handled
            System argument 2 - Action to be performed on a dag (create, import, delete)
            
    """
    parser = argparse.ArgumentParser(description='Run various DAG related commands')
    parser.add_argument('--wf-name',
                        type=str,
                        default='primary',
                        help='workflow name which will be the DAG base workflow')
    parser.add_argument('--action',
                        type=str,
                        default='create',
                        help='DAG action (create / import / delete')

    args = parser.parse_args()

    dag = Dag(args.wf_name)

    if args.action == 'create':
        dag.create_dag()

    elif args.action == 'import':
        dag.import_dag()

    elif args.action == 'delete':
        dag.delete_dag()

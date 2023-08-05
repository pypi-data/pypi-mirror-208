## Part 4 - Setting up a new batch project.{#quick_start4} 


### Step 1 - Setting up your environment

#### Install requirements:
After venv is ready, and the framework is installed, 
we can install batch related requirements:

    pip install -r batch_files/requirements.txt

#### Log in to gcloud
Make sure that you're logged in to gcloud, as many of the actions rely on that:

    gcloud auth login
    gcloud auth login --update-adc

#### Switch to research project
    gcloud config set project dozi-data-science-research-1

#### Update configuration file
Make sure that the project is configured adequately and that it suits your needs.
Please browse:

    <root_folder>/batch_files/batch_config.json

#### Monitor
Please note that any of the following stages can be monitored by visiting the GCP webpage and 
browsing through the different products (DataProc, Composer, Storage)

### Step 2 - Write your code

#### Creating new workflows / stages

Two main workflows are created upon project generation:
1. Primary - This is the main workflow intended for data science work
2. Trainer - This workflow is intended for model training

#### Adding new workflow
    dsf-cli generate workflow <workflow name>
This will create a new workflow directory under "workflows", and will contain a stage directory, 
a requirement file, and a configuration file relevant to the new workflow.
Relevant sections will be added to the setup.py file, and to the build.sh file

#### Adding a new stage
    dsf-cli batch-stage create <stage name>
After running this command, you will be requested to state which workflow is this stage supposed to run under. 
A new directory will be created under the "stages" folder in the chosen workflow, along with a main.py file, in which 
the implementation should be made.
A place will be ready for your new stage in the <wf_name>_config.json file, please use it to determine
stage order and prerequisites

### Step 3 - Run your code

#### Setting up a cluster - Optional
The framework allows several actions regarding DataProc clusters:

    dsf-cli dataproc-cluster create # Create a DataProc cluster
    dsf-cli dataproc-cluster stop # Stop a running cluster
    dsf-cli dataproc-cluster start # Start a stopped cluster
    dsf-cli dataproc-cluster delete # Delete a cluster. (Used for configuration changes)
    dsf-cli dataproc-cluster connect # SSH connection to the master node
This stage is optional since a temporary cluster will be created when the workflow template is instantiated, assuming 
that no cluster existed when the workflow template was created.

#### Uploading relevant files to appropriate buckets
In order to make sure that all needed files are present, please follow these steps:
1. Copy all relevant .jar files to batch_files/jars
2. Pack your project into a .zip file by running:


    python batch_files/scripts/build.sh
               
Naturally, you should make sure that the build.sh file does work properly.

3. Upload files to configured bucket by running:

    
    dsf-cli upload-batch-files <wf_name> <file_type> # options are: [all, jars, stages, whl, cluster-init]

#### Creating a workflow template
The framework allows several actions regarding DataProc Workflows:

    dsf-cli workflow-template <wf_name> create -> Create and upload the template
    dsf-cli workflow-template <wf_name> create_yaml -> Create a yaml file
    dsf-cli workflow-template <wf_name> instantiate -> Run a workflow
    dsf-cli workflow-template <wf_name> delete -> Delete a workflow

A basic code for creating workflow template is provided upon project generation.


#### Instantiating the workflow template - Dev mode
In order to go from template to an actual workflow and go through the stages, 
one should instantiate it. As a developer, you might want to do so immediately, 
rather than going through the DAG process. So, just run the command from the previous paragraph with 
the "instantiate" action. You should see your workflow running and the jobs being processed.

#### Instantiating the workflow template - DAG
The framework provides a basic DAG, which defaults to a daily activity and starts 
as paused, assuming that you're not under staging / production environments.

In order to create it, please run:

    dsf-cli dag <wf_name> create

Once done, please import it into the GCP Composer by running:
    
    dsf-cli dag <wf_name> import

Please note that since this DAG starts as "paused", you would need to activate it first, either by
entering the Airflow GUI from the GCP Composer page, or any other way you can come up with...

#### Running a single stage - Optional
If you wish to run a single stage without having to deal with the entire workflow, please make sure
that a cluster is up and running, and run:

    dsf-cli batch-stage run <stage_name>

# Good luck!

import ast
from typing import List

import click
import os
import shutil
import re
import platform
import subprocess
import site
import webbrowser
import hashlib
from datetime import datetime
from pathlib import Path
from ujson import load as json_load
from ujson import dumps as json_dumps
from ujson import dump as json_dump
from dsframework.documentation.scripts import doxygen_handler

isWindows = platform.system() == 'Windows'

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

__proj_root__ = os.path.abspath(os.getcwd())

directories = {
    'main': '',
    'pipeline': '',
    'artifacts': '',
    'models': '',
    'vocabs': '',
    'other': '',
    'preprocessor': '',
    'predictables': '',
    'predictors': '',
    'forcers': '',
    'postprocessor': '',
    'schema': '',
    'tester': '',
    'test_schema': '',
    'trainer': '',
    'server': '',
    'dsp': '',
    'documentation': ''
}


##
# @file
# @brief This file defines and implements the framework CLI. It helps us to:\n
#        Create: Project/Forcer/Predictable/Tester-files/Deploy-files/Cloud-Eval-Files  \n
#        Run   : Server / Evaluation (CSV,Cloud) \n


class AliasedGroup(click.Group):
    """! AliasedGroup implements click.Group base class."""

    ##
    # @hidecallgraph @hidecallergraph
    def get_command(self, ctx, cmd_name):
        try:
            cmd_name = ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)


@click.group(cls=AliasedGroup)
@click.version_option(package_name='dsFramework')
def cli():
    """
    DS framework cli

    ** How to use **

    g = generate

    Create project
    ==============
    dsf-cli g project my-new-project

    Generate forcer
    ===============
    dsf-cli g forcer my-new-forcer

    Generate predictable
    ====================
    dsf-cli g predictable my-new-predictable

    Create files
    ===================
    dsf-cli create-files [tester / deploy / cloud_eval / documentation / batch / trainer]

    Create Mlops dir
    ====================
    dsf-cli create-mlops

    run server
    ==========
    dsf-cli run-server

    run evaluation on a csv input
    =============================
    dsf-cli evaluate input-csv-file batch-size

    ==============
    Documentation
    ==============

    Generate documentation
    ======================
    dsf-cli generate documentation full

    Generate documentation - without base classes:
    ==============================================
    dsf-cli generate documentation simple

    Show documentation
    ==================
    dsf-cli show-documentation

    Upload documentation
    ====================
    dsf-cli upload-documentation

    ========================
    Batch project abilities
    ========================

    Workflow Creation
    =================
    dsf-cli generate workflow <new_workflow_name>

    DataProc Cluster Manipulation
    =============================
    dsf-cli dataproc-cluster <create / stop / start / delete / connect>

    Batch Stage Manipulation
    ========================
    dsf-cli batch-stage <create / run> my-stage

    Workflow Template Manipulation
    ==============================
    dsf-cli workflow-template <create / create_yaml / delete / instantiate>

    DAG Manipulation
    ================
    dsf-cli dag <create / import / delete>

    Upload files to bucket
    ======================
    dsf-cli upload-batch-files <jars, stages, whl , cluster_init, all>

    Miscellaneous
    Create sonar scanner properties file:
    ====================================
    dsf-cli create-sonar-file current_project_repo_name

    Install requirements for trainer
    ================================
    dsf-cli install-trainer-packages

    Install documentation doxygen
    =============================
    dsf-cli install-documentation-requirements

    Deploy project to GAE
    =====================
    dsf-cli deploy_service_to_gae
    """


# @click.option("--type", prompt="type", help="type of component")
# @click.option("--project_name", prompt="project_name", help="project_name")
# def apis(type, project_name):


@cli.command()
@click.argument('gen_type')
@click.argument('project_name')
def generate(gen_type, project_name):
    """! Build a generation function from the incoming gen_type.
        Args:
            gen_type: A string containing one of the following: [project / forcer / predictable / documentation / stage]
            project_name: A string declaring our project name
    """
    try:
        f = globals()["generate_%s" % gen_type]
    except Exception as e:
        click.echo('type ' + gen_type + ' not found')
        return
    f(project_name)


@cli.command()
@click.argument('file_type')
def create_files(file_type):
    """! Build a file creation function from the incoming file type.
        Args:
            file_type: A string containing one of the following:
                [tester / deploy / cloud_eval / documentation / batch / trainer]
    """
    try:
        f = globals()["create_%s_files" % file_type]
    except Exception as e:
        click.echo('type ' + file_type + ' not found')
        return
    f()


@cli.command()
def create_mlops():
    """! Copy Mlops directory from DSF """
    source_dir = os.path.join(__location__, 'dsframework/cli/mlops/')
    target_dir = os.path.join(os.path.abspath(os.getcwd()), 'mlops')
    shutil.copytree(source_dir, target_dir)


@cli.command()
def run_server():
    """! Start a uvicorn server by running /server/main.py """
    currentPipelineFolder = __proj_root__
    currentParentFolder = os.path.join(currentPipelineFolder, "..")
    os.environ["PYTHONPATH"] = currentPipelineFolder
    folder = currentPipelineFolder + '/server/main.py'
    subprocess.call('python ' + folder, shell=True)


@cli.command()
@click.argument('tag')
@click.argument('env', default="prd")
def cloud_eval(tag, env):
    # """Cloud evaluation running on AWS """
    currentPipelineFolder = __proj_root__
    currentParentFolder = os.path.join(currentPipelineFolder, "..")
    os.environ["PYTHONPATH"] = currentPipelineFolder
    folder = currentPipelineFolder + '/tester/dsp/get_model_options.py'
    output = subprocess.check_output('python ' + folder + ' ' + env, shell=True, encoding='utf-8').strip()
    if output:
        # print('output', output)
        l = output.split('\n')
        m = l[-1]
        try:
            l = ast.literal_eval(m)
            o = l[0]
            model = {
                'name': o['name'],
                'id': o['id'],
                'repo': o['repo'],
            }
            folder = currentPipelineFolder + '/tester/dsp/get_dataset_options.py'
            output = subprocess.check_output(
                'python ' + folder + ' ' + env + ' ' + model['name'] + ' ' + str(model['id']),
                shell=True, encoding='utf-8').strip()
            l = output.split('\n')
            m = l[-1]
            l = ast.literal_eval(m)
            selected = let_user_pick(l)
            # print('selected', selected)
            if not selected == None:
                selected_dataset = l[selected]
                # print('model',model)
                # print('selected_dataset', selected_dataset)
                folder = currentPipelineFolder + '/tester/dsp/add_experiment.py'
                subprocess.call(('dvc_push.sh'), shell=True)
                output = subprocess.call(('python', folder, env, json_dumps(model), json_dumps(selected_dataset), tag),
                                         shell=True)
                print('you can see your experiment in que')
            else:
                print('selection does not exist')
        except Exception as e:
            print(m)
    else:
        print('could not get models')


def create_deploy_files():
    """! Create deploy files (created through 'Create project', but can be used as a standalone function) """
    copy_deploy_files('')


def create_cloud_eval_files():
    """! Create cloud evaluation files (created through 'Create project', but can be used as a standalone function) """
    copy_cloud_eval_files(__proj_root__)


def create_tester_files():
    """! Create tester files (created through 'Create project', but can be used as a standalone function) """
    create_tester_env()


def create_documentation_files():
    """! Create documentation files (created through 'Create project', but can be used as a standalone function) """
    project_name = os.path.basename(os.getcwd())
    copy_documentation_files(os.path.join(directories['main'], 'documentation'))
    update_doc_configuration(project_name, os.path.join(directories['main'], 'documentation'))


def create_batch_files():
    """! Create batch files (created through 'Create project', but can be used as a standalone function) """
    copy_batch_files(directories['main'])


def create_trainer_files():
    """! Create trainer files (created through 'Create project', but can be used as a standalone function) """
    copy_trainer_files()


@cli.command()
@click.argument('wf_name')
@click.argument('action')
def dataproc_cluster(wf_name: str, action: str):
    """! Handle cluster action, either create,  start, stop, delete, or connect to the Dataproc cluster
            Args:
                wf_name: Relevant workflow that affects cluster configuration
                action: an action to perform, chosen from: {create, start, stop, delete, connect}
    """
    valid_actions = {'create', 'start', 'connect', 'stop', 'delete'}
    if action not in valid_actions:
        print(f"Can't determine action of type: {action}. Please use one of: {valid_actions}")
        return

    if not workflow_exists(wf_name):
        click.echo(f"Chosen workflow ({wf_name}) does not exist. Please choose a different workflow")
        return

    batch_helper = config_batch_helper(wf_name)

    if action == 'create':
        # Create DataProc cluster according to project specific configuration
        batch_helper.create_dataproc_cluster()
    elif action == 'start':
        # Start an existing DataProc cluster according to project specific configuration
        batch_helper.start_dataproc_cluster()
    elif action == 'connect':
        # Connect via ssh to an existing DataProc cluster according to project specific configuration.
        # Connection will be made to the master node
        batch_helper.connect_dataproc_cluster()
    elif action == 'stop':
        # Stop an existing DataProc cluster according to project specific configuration
        batch_helper.stop_dataproc_cluster()
    elif action == 'delete':
        # Delete an existing DataProc cluster according to project specific configuration.
        # Since we can't update certain parameters on an existing cluster, we need the option
        # to delete it
        batch_helper.delete_dataproc_cluster()


def update_config_file(stage_name: str, workflow_name: str, prerequisites: List[str]):
    """! Update relevant workflow configuration file with new stage
    @verbatim
    Args:
            stage_name: Stage name to be used
            workflow_name: Relevant workflow that will handle the new stage
            prerequisites: A list of stages that the new stage depends on
    @endverbatim
    """

    config_path = os.path.join(__proj_root__,
                               f'batch_files/workflows/{workflow_name}_workflow/config_{workflow_name}.json')

    stage_dict_entry = {"stage_name": stage_name,
                        "prerequisites": prerequisites}

    # Open json file, load to dictionary, update it and save it back
    with open(config_path, 'r+') as config_file:
        data = json_load(config_file)
        data['workflow_stages'].append(stage_dict_entry)
        config_file.seek(0)  # <--- should reset file position to the beginning.
        json_dump(data, config_file, indent=4)
        config_file.truncate()  # remove remaining part


def create_batch_stage(stage_name: str = '', workflow_name: str = ""):
    """! Generating new stage for a given workflow
    @verbatim
    Args:
            stage_name: Stage name to be used when creating files / folders / classes.
            workflow_name: Relevant workflow that will handle the new stage
    @endverbatim
    """
    stage_name = clean_name(stage_name)
    workflow_name = clean_name(workflow_name)

    if not validate_stage(stage_name, workflow_name):
        return

    create_stage_files_from_template(stage_name, workflow_name)

    # TBD: Should the prerequisites be validated, or this is a user responsibility?
    prerequisites = click.prompt('Please enter dependency stages (separate with comma)',
                                 type=str,
                                 default="",
                                 show_default=False)

    prerequisite_list = [] if prerequisites == "" else [list_value.strip() for list_value in prerequisites.split(',')]

    update_config_file(stage_name, workflow_name, prerequisite_list)

    click.echo(f'Created {stage_name} stage under {workflow_name} Workflow')


@cli.command()
@click.argument('action')
@click.argument('stage_name')
def batch_stage(action: str, stage_name: str):
    """! Handle batch stages action, either create or run a specific stage
        Args:
             action: an action to perform, chosen from: {create, create_yaml, instantiate, delete}
             stage_name: Name for the newly created stage, or the stage to be run on an existing cluster
    """
    valid_actions = {'create', 'run'}
    if action not in valid_actions:
        print(f"Can't determine action of type: {action}. Please use one of: {valid_actions}")
        return

    relevant_workflow = click.prompt('Please enter a valid workflow name', type=str)

    if action == 'create':
        # Create a batch stage
        create_batch_stage(stage_name, relevant_workflow)
    elif action == 'run':
        # Run specific stage on an existing Dataproc cluster
        batch_helper = config_batch_helper(relevant_workflow)
        batch_helper.run_single_stage(stage_name)


@cli.command()
@click.argument('wf_name')
@click.argument('action')
def workflow_template(wf_name: str, action: str):
    """! Handle workflow action, either create, instantiate or delete the template
        Args:
            wf_name: Relevant workflow to perform the selected action
            action: An action to perform, chosen from: {create, create_yaml, instantiate, delete}
    """
    valid_actions = {'create', 'create_yaml', 'delete', 'instantiate'}
    if action not in valid_actions:
        click.echo(f"Can't determine action type: {action}. Please use one of: {valid_actions}")
        return

    if not workflow_exists(wf_name):
        click.echo(f"Chosen workflow ({wf_name}) does not exist. Please choose a different workflow")
        return

    current_folder = __proj_root__

    os.environ["PYTHONPATH"] = current_folder
    workflow_folder = current_folder + '/batch_files/workflows/workflow.py'
    basic_command = 'python ' + workflow_folder

    click.echo(f"Attempting to {action} a workflow template")
    subprocess.call(basic_command + ' --wf-name ' + wf_name + ' --action ' + action, shell=True)


@cli.command()
@click.argument('wf_name')
@click.argument('action')
def dag(wf_name: str, action: str):
    """! Handle DAG actions, either create, delete, or import a DAG
    Once imported, it will start as paused and will be set up for a daily activation
        Args:
            wf_name: Relevant workflow to perform the selected action
            action: an action to perform, chosen from: {create, import, delete}
    """
    valid_actions = {'create', 'import', 'delete'}
    if action not in valid_actions:
        click.echo(f"Can't determine action type: {action}. Please use one of: {valid_actions}")
        return

    if not workflow_exists(wf_name):
        click.echo(f"Chosen workflow ({wf_name}) does not exist. Please choose a different workflow")
        return

    current_folder = __proj_root__

    os.environ["PYTHONPATH"] = current_folder
    dag_folder = current_folder + '/batch_files/workflows/dag.py'
    basic_command = 'python ' + dag_folder

    click.echo(f"Attempting to {action} a DAG")
    subprocess.call(basic_command + ' --wf-name ' + wf_name + ' --action ' + action, shell=True)


@cli.command()
@click.argument('wf_name')
@click.argument('file_type')
def upload_batch_files(wf_name: str, file_type: str):
    """! Upload all files needed for a batch project to the predefined bucket
        Args:
            wf_name: Relevant workflow to perform the selected action
            file_type: String containing the types of files to upload (jars, stages, whl , cluster_init, or "all")
    """
    if not workflow_exists(wf_name):
        click.echo(f"Chosen workflow ({wf_name}) does not exist. Please choose a different workflow")
        return

    batch_helper = config_batch_helper(wf_name)
    batch_helper.upload_files_to_bucket(file_type)


def config_batch_helper(wf_name: str):
    """! Configure the batch file helper for a variety of cli actions
        Args:
            wf_name: Relevant workflow to perform the selected action
        Returns:
            ZIDSBatchHelper: Instantiation of the batch helper class
    """
    from dsframework.cli.batch.batch_helper_functions import ZIDSBatchHelper

    batch_helper_cls = None

    with open(__proj_root__ + '/batch_files/batch_config.json') as batch_cfg_file:
        batch_config = json_load(batch_cfg_file)

    with open(__proj_root__ + f"/batch_files/workflows/{wf_name}_workflow/config_{wf_name}.json") as wf_cfg_file:
        wf_config = json_load(wf_cfg_file)

    config_dict = {**batch_config, **wf_config}

    batch_helper_cls = ZIDSBatchHelper(config_dict)

    return batch_helper_cls


@cli.command()
@click.argument('repo_name')
def create_sonar_file(repo_name: str):
    """! Create a sonar scanner file.

    Args:
        repo_name: name of your repository.
    """

    data = "sonar.projectKey=dozi_" + repo_name
    create_file(os.path.join(__proj_root__, "sonar-scanner.properties"), data)


@cli.command()
@click.argument('csv_file_path')
@click.argument('batch_size')
def evaluate(csv_file_path, batch_size):
    """! Quick 'Initial test' to check the module.

    @verbatim
    Args:
        csv_file_path: CSV file path.
        batch_size: The size that will be taken every iteration from the CSV - in order to feed the model.
    @endverbatim
    """

    if os.path.isfile(csv_file_path):
        current_pipeline_folder = __proj_root__
        os.environ["PYTHONPATH"] = current_pipeline_folder
        folder = current_pipeline_folder + '/tester/general_tester.py'
        subprocess.call('python ' + folder + ' ' + csv_file_path + ' ' + batch_size, shell=True)
    else:
        click.echo('file: ' + csv_file_path + ' not found')


@cli.command()
def show_documentation():
    """! Opens a browser and show the local project documentation."""
    launch_doc_webbrowser()


def launch_doc_webbrowser():
    current_pipeline_folder = __proj_root__

    current_doc_folder = os.path.join(current_pipeline_folder, "documentation")
    if os.path.isdir(os.path.join(current_pipeline_folder, "dsframework", "documentation")):
        current_doc_folder = os.path.join(current_pipeline_folder, "dsframework", "documentation")

    project_html_path = os.path.join(current_doc_folder, 'project_docs', 'html', 'index.html')
    if os.path.isfile(project_html_path):
        webbrowser.open('file://' + project_html_path)
    else:
        click.echo('Project documentation not found, please generate documentation using: \'dsf-cli generate '
                   'documentation full\'')


ALIASES = {
    "g": generate
}


def generate_project(project_name):
    """! Generating new project (with the relevant project_name)\n
    How to generate project :
    > dsf-cli g project my-new-project
    @verbatim
    Args:
            project_name: Project name will be used in the creation of the files.
    @endverbatim
    """
    # project_name = clean_name(project_name)
    click.echo('Generating project: ' + project_name)
    create_project(project_name)


def generate_forcer(file_name):
    """! Generate new forcer - can help us, if we need forcer on an existing project """
    file_name = clean_name(file_name)
    create_exist_pipeline_file('forcer', file_name)


def generate_predictable(file_name):
    """! Generate new predictable - can help us, if we need predictable on an existing project
    """
    file_name = clean_name(file_name)
    create_exist_pipeline_file('predictable', file_name)


def add_workflow_to_setup(workflow_name: str):
    """! Modify setup.py for the whl creation of batch projects
    @verbatim
    Args:
            workflow_name: Workflow to be added to the file
    @endverbatim
    """

    insert_string = f"if build_type == '{workflow_name}':\n\tdata = config + pipeline + batch_files + tester\n\n"
    setup_file_path = os.path.join(__proj_root__, "batch_files/setup.py")

    with open(setup_file_path, 'r+') as setup_fd:
        contents = setup_fd.readlines()
        if "# Additional workflows" in contents[-1]:  # Handle last line to prevent IndexError
            contents.append(insert_string)
        else:
            for index, line in enumerate(contents):
                if "# Additional workflows" in line and insert_string not in contents[index + 1]:
                    contents.insert(index + 1, insert_string)
                    break
        setup_fd.seek(0)
        setup_fd.writelines(contents)


def generate_workflow(workflow_name: str):
    """! Generating a new workflow to be used on GCP Dataproc
    @verbatim
    Args:
            workflow_name: Workflow to be created
    @endverbatim
    """

    click.echo('Generating workflow: ' + workflow_name)

    if not os.path.exists(os.path.join(__proj_root__, "batch_files")):
        click.echo("Couldn't find batch project folder, creating...")
        copy_batch_files(directories['main'])

    if workflow_exists(workflow_name):
        click.echo(f'Workflow "{workflow_name}" already exists. Please use a different name.')
        return

    workflow_path = os.path.join(__proj_root__, f"batch_files/workflows/{workflow_name}_workflow")

    # Create primary workflow folder
    os.mkdir(workflow_path)
    create_empty_init_file(workflow_path)

    # Create an empty stages folder
    stages_path = os.path.join(workflow_path, "stages")
    os.mkdir(stages_path)
    create_empty_init_file(stages_path)

    # Create an empty requirement file
    create_file(os.path.join(workflow_path, f"requirements_{workflow_name}.txt"), "")

    # Create configuration file from template
    data = read_template_file('batch/workflow_config', "json")
    data = data.replace('{name-your-wf}', workflow_name)
    data = data.replace('{name-your-service}', os.path.split(os.getcwd())[-1])

    create_file(os.path.join(workflow_path, f"config_{workflow_name}.json"), data)
    
    # Manipulate setup.py to include the new build type
    add_workflow_to_setup(workflow_name)


def workflow_exists(wf_name: str = ""):
    """! Checks if a workflow with the given name exists
        Args:
                wf_name: Workflow name to be validated
        Returns:
            True if workflow already exists, False otherwise
        """

    return os.path.exists(os.path.join(__proj_root__, f'batch_files/workflows/{wf_name}_workflow'))


def validate_stage(stage_name: str = "", workflow: str = ""):
    """! Checks if a stage with the given name is valid
    Args:
            stage_name: Stage name to be validated
            workflow: Workflow name to be validated
    Returns:
        True if stage can be created correctly, False otherwise
    """

    # Check workflow validity
    if not workflow_exists(workflow):
        click.echo(f'Workflow "{workflow}" does not exist. Please create or try a different workflow.')
        return False

    # Check stage validity
    if os.path.exists(os.path.join(__proj_root__, f'batch_files/workflows/{workflow}_workflow/stages/{stage_name}')):
        click.echo(f'Stage "{stage_name}" already exists for given workflow "{workflow}". Please use a different name.')
        return False

    return True


def generate_documentation(simple="full"):
    """! Document project CLI

        Usage:
            dsf-cli generate documentation full
    """
    if simple == 'full':
        click.echo('Documenting project .....')
    else:
        click.echo('Documenting project (without base).....')

    # Get folders
    current_pipeline_folder = __proj_root__
    current_doc_folder = os.path.join(current_pipeline_folder, "documentation")
    if os.path.isdir(os.path.join(current_pipeline_folder, "dsframework", "documentation")):
        current_doc_folder = os.path.join(current_pipeline_folder, "dsframework", "documentation")

    # Validity checks
    if not os.path.isfile(os.path.join(current_doc_folder, 'project_doxyfile')):
        click.echo("Documentation folder not found, please change directory to project root folder.")
        return

    venv_path = os.getenv('VIRTUAL_ENV')

    try:
        if simple == 'full':
            os.environ["EXCLUDE_PATH"] = get_exclude_string(venv_path)
        else:
            os.environ["EXCLUDE_PATH"] = venv_path
    except Exception as e:
        click.echo(f'Switching to simple: {e}')
        os.environ["EXCLUDE_PATH"] = venv_path

    click.echo(f'Creating project documentation in {os.path.join(current_doc_folder, "project_docs")}')

    try:
        # Run doxygen as subprocess
        subprocess.call('doxygen project_doxyfile', shell=True, cwd=current_doc_folder)
    except Exception as e:
        click.echo(f'Project documentation failed!, exception: {e}')
    else:
        click.echo('Project documentation done!')
        launch_doc_webbrowser()


def get_exclude_string(venv_path):
    packages_path = site.getsitepackages()  # Get packages folder.

    # Get list of packages to exclude, except 'dsframework'
    pkg_exclude_folders = get_excluded_path_list('(?!.*dsframework)', packages_path[0], 'folders')

    # Get list of scattered file in packages folder
    pkg_exclude_files = get_excluded_path_list('(?!.*api_cli.py)', packages_path[0], 'files')

    # Get a list of files and folders in dsframework, except 'base' folder.
    pkg_exclude_dsf = get_excluded_path_list('(?!.*base)', os.path.join(packages_path[0], 'dsframework'), 'both')

    # Get venv all the rest the folders to exclude, except 'venv/lib'
    exclude_venv = get_excluded_path_list('(?!.*lib)', venv_path, 'both')

    # Combine two lists to one string: exclude_folders and exclude_folders
    exclude_full_list = pkg_exclude_folders + exclude_venv + pkg_exclude_files + pkg_exclude_dsf
    exclude_string = " \\ ".join(map(str, exclude_full_list))  # Seperated by backslash

    return exclude_string


def get_excluded_path_list(regex_str, path, get_type):
    if get_type == 'folders':
        path_list = [os.path.join(path, name) for name in os.listdir(path)
                     if os.path.isdir(os.path.join(path, name))]
    elif get_type == 'files':
        path_list = [os.path.join(path, name) for name in os.listdir(path)
                     if os.path.isfile(os.path.join(path, name))]
    else:  # 'both'
        path_list = [os.path.join(path, name) for name in os.listdir(path)]

    if regex_str != '':
        regex = re.compile(regex_str)
        return list(filter(regex.match, path_list))
    else:
        return path_list


def zip_folder(local_documentation_folder, path_file_name):

    if os.path.isdir(local_documentation_folder):
        if os.listdir(local_documentation_folder):
            shutil.make_archive(path_file_name, 'zip', local_documentation_folder)


def hash_file(file_path):

    hash_code = hashlib.sha256()

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hash_code.update(chunk)

    return hash_code.hexdigest()


@cli.command()
def upload_documentation():
    """! Upload project documentation CLI

        Usage:
            dsf-cli upload-documentation
    """

    # Set folders
    current_working_path = os.getcwd()
    project_name = os.path.split(current_working_path)[1]
    current_doc_folder = os.path.join(current_working_path, 'documentation', 'project_docs')
    local_upload_folder = os.path.join(current_working_path, 'documentation', 'upload')
    html_folder_name = 'html'

    google_gs_path = 'gs://dozi-stg-ds-apps-1-ds-apps-ds-portal/documentation/'

    project_gs_folder = f'{google_gs_path}'

    if project_name == 'ds-framework':
        current_doc_folder = os.path.join(current_working_path, 'dsframework', 'documentation', 'project_docs')
        local_upload_folder = os.path.join(current_working_path, 'dsframework', 'documentation', 'upload')

    # Validity checks
    if not os.path.isfile(os.path.join(current_doc_folder, html_folder_name, 'index.html')):
        click.echo('Documentation folder not found, please change directory to project root folder.')
        return

    local_documentation_folder = os.path.join(current_doc_folder, html_folder_name)

    if os.path.isdir(local_upload_folder):
        shutil.rmtree(local_upload_folder)

    os.mkdir(local_upload_folder)

    zip_folder(local_documentation_folder, os.path.join(local_upload_folder, project_name))

    hash_code = hash_file(os.path.join(local_upload_folder, project_name) + '.zip')
    with open(os.path.join(local_upload_folder, f'{project_name}_hash.txt'), 'w') as file_hash:
        file_hash.write(hash_code)

    # Upload current documentation
    click.echo(f'Uploading {project_name} documentation started....')

    call_gsutil_command(f'gsutil -m cp -r {local_upload_folder} {project_gs_folder}',
                        project_name, current_doc_folder, 'Uploading documentation')

    click.echo(f'Uploading {project_name} documentation done!!!')


def call_gsutil_command(gsutil_command, project_name, working_folder, command_desc):
    click.echo(f'{command_desc} {project_name} ....')

    try:
        subprocess.call(gsutil_command, shell=True, cwd=working_folder)
    except Exception as e:
        click.echo(f'{command_desc} failed with exception: {e}')
        return
    else:
        click.echo(f'{command_desc} done!')


def clean_name(name):
    """! Change the name from 'word1-word2' --> 'word1_word2' """
    name = name.replace('-', '_')
    return name


def create_folders(project_name):
    """! Create all needed folders for the new project creation
    @verbatim
    Args:
        project_name: Project name
    @endverbatim
    """

    global directories
    directories['main'] = project_name
    if not os.path.exists(directories['main']):
        os.mkdir(directories['main'])

    create_main_folders('config', 'main')
    create_main_folders('pipeline', 'main')
    create_main_folders('artifacts', 'pipeline')
    create_main_folders('models', 'artifacts')
    create_main_folders('vocabs', 'artifacts')
    # create_main_folders('other', 'artifacts')
    create_main_folders('preprocessor', 'pipeline')
    create_main_folders('predictables', 'pipeline')
    create_main_folders('predictors', 'pipeline')
    create_main_folders('forcers', 'pipeline')
    create_main_folders('postprocessor', 'pipeline')
    create_main_folders('schema', 'pipeline')
    create_main_folders('tester', 'main')
    create_main_folders('test_schema', 'tester')
    create_main_folders('dsp', 'tester')
    create_main_folders('trainer', 'main')
    create_main_folders('training_output', 'trainer')
    create_main_folders('pl_wrapper', 'trainer')
    create_main_folders('server', 'main')


def create_project(project_name):
    """! Create project from templates.
    @verbatim
    Args:
        project_name: Project name
    @endverbatim
    """

    create_folders(project_name)
    original_project_name = project_name
    project_name = clean_name(project_name)

    # Create pipeline files
    create_pipeline_file(project_name, directories['artifacts'], 'shared_artifacts')
    create_pipeline_file(project_name, directories['preprocessor'], 'preprocess')
    create_pipeline_file(project_name, directories['predictors'], 'predictor')
    create_pipeline_file(project_name, directories['forcers'], 'forcer')
    create_pipeline_file(project_name, directories['postprocessor'], 'postprocess')
    create_pipeline_file(project_name, directories['predictables'], 'predictable')
    create_pipeline_file(project_name, directories['pipeline'], 'pipeline')
    create_pipeline_file(project_name, directories['main'], 'pipeline_test', False)

    # Create schema files
    create_schema_file(project_name, directories['schema'], 'inputs')
    create_schema_file(project_name, directories['schema'], 'outputs')
    create_schema_file(project_name, directories['schema'], '__init__', False)

    # Create tester files
    create_tester_file(project_name, directories['tester'], 'general_tester', False)
    create_tester_file(project_name, directories['tester'], 'evaluator', False)
    create_empty_init_file(directories['tester'])
    create_schema_file(project_name, directories['test_schema'], 'test_input', False)
    create_schema_file(project_name, directories['test_schema'], 'test_output', False)
    create_empty_init_file(directories['test_schema'])
    create_dsp_file(original_project_name, directories['dsp'], 'get_model_options', False)
    create_dsp_file(original_project_name, directories['dsp'], 'get_dataset_options', False)
    create_dsp_file(original_project_name, directories['dsp'], 'add_experiment', False)
    create_empty_init_file(directories['dsp'])

    # Create trainer files
    create_trainer_file(project_name, directories['pl_wrapper'], 'custom_dataset', False, from_folder='pl_wrapper')
    create_trainer_file(project_name, directories['pl_wrapper'], 'data_module', False, from_folder='pl_wrapper')
    create_trainer_file(project_name, directories['pl_wrapper'], 'iterable_dataset', False, from_folder='pl_wrapper')
    create_trainer_file(project_name, directories['pl_wrapper'], 'plmodel', False, from_folder='pl_wrapper')
    create_trainer_file(project_name, directories['pl_wrapper'], 'network_module', False, from_folder='pl_wrapper')
    create_trainer_file(project_name, directories['pl_wrapper'], 'save_onnx', False, from_folder='pl_wrapper')

    create_empty_init_file(directories['pl_wrapper'])
    create_trainer_file(project_name, directories['trainer'], 'comparison', False)
    create_trainer_file(project_name, directories['trainer'], 'config', False)
    create_trainer_file(project_name, directories['trainer'], 'data', False)
    create_trainer_file(project_name, directories['trainer'], 'dataset_preparation', False)
    create_trainer_file(project_name, directories['trainer'], 'model', False)
    create_trainer_file(project_name, directories['trainer'], 'test', False)
    create_trainer_file(project_name, directories['trainer'], 'train', False)
    create_trainer_file(project_name, directories['trainer'], 'main', False)
    create_empty_init_file(directories['trainer'])
    source_path = os.path.join(__location__, 'dsframework/cli/trainer/requirements_trainer.txt')
    shutil.copyfile(source_path, directories['trainer'] + '/requirements_trainer.txt')

    # Create server files
    create_server_file(project_name, directories['server'], 'main', False)
    create_server_file(project_name, directories['server'], 'test_server_post', False)
    create_server_file(project_name, directories['server'], 'pool', False)
    create_server_file(project_name, directories['server'], 'token_generator', False)
    create_server_file(project_name, directories['server'], '__init__', False)

    # Copy logger files to newly created project
    copy_logger_files(project_name)

    create_project_config_json()
    create_project_gitignore()
    create_server_config_json()
    copy_deploy_files(directories['main'])
    copy_cloud_eval_files(directories['main'])
    copy_batch_files(directories['main'])
    copy_documentation_files(os.path.join(directories['main'], 'documentation'))
    update_doc_configuration(project_name, os.path.join(directories['main'], 'documentation'))

    change_to_project_dir()
    run_dvc_init()
    run_git_init()


def create_main_folders(target_dir, base_dir):
    """! Create folder if not already exists
    @verbatim
    Args:
        target_dir: the new folder to create
        base_dir  : where we want to create the new folder.
    @endverbatim
    """

    global directories
    directories[target_dir] = directories[base_dir] + '/' + target_dir
    if not os.path.exists(directories[target_dir]):
        os.mkdir(directories[target_dir])


def create_pipeline_file(project_name, folder, pipeline_type, create_init=True):
    """! Takes the template file and replace it with new one with project_name
    @verbatim
    Args:
        project_name : The project name
        folder       : The folder we want to create the new file.
        pipeline_type : File type in the pipeline.
        create_init(=True): Create init file - if doesnt exist.
    @endverbatim
    """

    data = read_template_file(pipeline_type)
    replace_in_template_and_create_file(project_name, folder, pipeline_type, data, create_init)


def create_schema_file(project_name, folder, pipeline_type, create_init=True):
    """! Create schema files (read the template and replace it )
    @verbatim
    Args:
        project_name : The project name
        folder       : The folder we want to create the new file.
        pipeline_type : File type. TODO change pipelineType name
        create_init(=True): Create init file - if doesnt exist.
    @endverbatim
    """
    data = read_template_file('schema/' + pipeline_type)
    replace_in_template_and_create_file(project_name, folder, pipeline_type, data, create_init)


def create_server_file(project_name, folder, pipeline_type, create_init=True):
    """! Create server file (read the template and use him to create the new file)
    @verbatim
    Args:
        project_name : The project name
        folder       : The folder we want to create the new file.
        pipeline_type : File type. TODO change pipelineType name
        create_init(=True): Create init file - if doesnt exist.
    @endverbatim
    """
    data = read_template_file('tester/server/' + pipeline_type)
    replace_in_template_and_create_file(project_name, folder, pipeline_type, data, create_init)


def create_tester_file(project_name, folder, test_file_type, create_init=True):
    """! Create tester file (read the template and use him to create the new file)
    @verbatim
    Args:
        project_name   : The project name.
        folder         : The folder we want to create the new file.
        test_file_type : File type.
        create_init(=True): Create init file - if doesnt exist.
    @endverbatim
    """
    data = read_template_file('tester/' + test_file_type)
    replace_in_template_and_create_file(project_name, folder, test_file_type, data, create_init)


def create_trainer_file(project_name, to_folder, test_file_type, create_init=True, from_folder=''):
    """! Create trainer file (read the template and use him to create the new file)
    @verbatim
    Args:
        project_name   : The project name.
        to_folder      : The folder we want to create the new file in.
        test_file_type : File type.
        create_init(=True): Create init file - if it doesn't exist.
        from_folder    : The folder from which we read the template file
    @endverbatim
    """

    # data = read_template_file('trainer/' + test_file_type)
    data = read_template_file(os.path.join('trainer', from_folder, test_file_type))
    replace_in_template_and_create_file(project_name, to_folder, test_file_type, data, create_init)


def create_dsp_file(project_name, folder, test_file_type, create_init=True):
    """! Create DSP file (read the template and use him to create the new file)
    @verbatim
        Args:
            project_name   : The project name.
            folder         : The folder we want to create the new file.
            test_file_type : File type.
            create_init(=True): Create init file - if doesnt exist.
    @endverbatim
    """
    data = read_template_file('tester/dsp/' + test_file_type)
    replace_in_template_and_create_file(project_name, folder, test_file_type, data, create_init)


def create_exist_pipeline_file(type, fileName):
    """! Create a new component in the pipeline and integrate it (for example forcer or predictable)
    @verbatim
    Args:
        type      : New component type (forcer or predictable)
        fileName  : New file name.
    @endverbatim
    """

    pipelineType = type + 's'
    folder = 'pipeline/' + pipelineType
    if os.path.exists(folder):
        data = read_template_file(type)
        fileNameNoUnderscore = to_capitalize_no_underscore(fileName)
        className = fileNameNoUnderscore + type.capitalize()
        currentPipelineFolder = os.path.basename(os.getcwd())
        currentDir = folder.replace('/', '.')

        data = data.replace('generatedClass', className)

        new_file = folder + "/" + fileName + ".py"
        current_init_file = folder + "/__init__.py"
        new_init_export = "from " + '.' + fileName + " import " + className

        create_file(new_file, data)
        create_init_file(current_init_file, new_init_export)
        inject_to_pipeline(fileName, type, className, new_init_export)
    else:
        print('please create a project and go to project location first')
    pass


def create_stage_files_from_template(stage_name: str = "", workflow_name: str = ""):
    """! Create all needed folders and files for the new stage
    @verbatim
    Args:
        stage_name: Stage name
        workflow_name: Workflow that this stage belongs to
    @endverbatim
    """

    data = read_template_file('batch/stage')
    stage_directory_name = os.path.join(__proj_root__,
                                        f'batch_files/workflows/{workflow_name}_workflow/stages/{stage_name}')
    os.mkdir(stage_directory_name)
    replace_in_stage_template_and_create_file(stage_name, stage_directory_name, workflow_name, data)


def create_tester_env():
    """! This function will create a testing environment, if one does not already exist in the project.
    It will create the testing, evaluation, and relevant schema files.
    """

    project_name = os.getcwd().split('/')[-1]
    dst_folder = 'tester/'
    schema_dst_folder = 'tester/test_schema/'
    dsp_dst_folder = 'tester/dsp/'
    tester_file_list = ["tester/general_tester",
                        "tester/evaluator",
                        "schema/test_input",
                        "schema/test_output",
                        "tester/dsp/add_experiment",
                        "tester/dsp/get_dataset_options",
                        "tester/dsp/get_model_options"]

    if not os.path.exists(dst_folder):
        os.mkdir(dst_folder)
        os.mkdir(schema_dst_folder)
        os.mkdir(dsp_dst_folder)

        for filename_with_path in tester_file_list:
            file_only = filename_with_path.split('/')[-1]
            parent_folder = filename_with_path.split('/')[-2]
            if parent_folder == 'schema':
                dst_folder = schema_dst_folder
            elif parent_folder == 'dsp':
                dst_folder = dsp_dst_folder

            data = read_template_file(filename_with_path)

            clean_project_name = clean_existing_project_name(project_name)
            filename_no_underscore = to_capitalize_no_underscore(file_only)

            class_name = clean_project_name + filename_no_underscore

            data = data.replace('generatedClass', class_name)
            data = data.replace('generatedProjectName', clean_project_name)

            new_file = dst_folder + "/" + file_only + ".py"
            create_file(new_file, data)

            # Test schema does not use generated class name for now, so this code should be modified before uncommenting
            # current_init_file = dst_folder + "/" + "__init__.py"
            # new_init_export = "from " + dst_folder.replace('/', '.') + "." + file_only + " import " + class_name
            # create_init_file(current_init_file, new_init_export)
    else:
        print('Tester folder Already exists. If you wish to recreate, please erase folder and retry')
    pass


def read_template_file(filename: str, file_type: str = "py"):
    """! Read \<filename\>_template.py  from the cli dir """
    with open(os.path.join(__location__, 'dsframework/cli/' + filename + f"_template.{file_type}"), 'r') as file:
        data = file.read()
        return data


def read_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        return data


def write_to_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)
        file.close()


def replace_in_template_and_create_file(project_name, folder, file_name, data, with_init_file):
    """! Get & Replace the template file and create new one with project_name
    @verbatim
    Args:
        project_name : The project name
        folder       : The folder we want to create the new file.
        file_name : Which File.
        data         : The template file.
        with_init_file(=True): Create init file if doesn't exist.
    @endverbatim
    """

    pipeline_type_no_underscore = to_capitalize_no_underscore(file_name)
    project_name_no_underscore = to_capitalize_no_underscore(project_name)
    class_name = project_name_no_underscore + pipeline_type_no_underscore
    class_name_for_base_object = project_name_no_underscore + pipeline_type_no_underscore
    current_dir = folder.replace('/', '.')
    current_base_dir = directories['main'].replace('/', '.')
    current_pipeline_dir = directories['pipeline'].replace('/', '.')

    data = data.replace('generatedClassName', class_name_for_base_object)
    data = data.replace('generatedClass', class_name)
    data = data.replace('original_project_name', project_name)
    data = data.replace('generatedProjectName', project_name_no_underscore)
    data = data.replace('generatedDirectory', current_dir)
    data = data.replace('generatedBaseDir', current_base_dir)
    data = data.replace('generatedPipelineDir', current_pipeline_dir)

    new_file = folder + "/" + file_name + ".py"
    create_file(new_file, data)

    if with_init_file:
        new_init_file = folder + "/__init__.py"
        new_init_export = "from " + '.' + file_name + " import " + class_name
        create_init_file(new_init_file, new_init_export)


def replace_in_stage_template_and_create_file(stage_name: str, folder: str, workflow_name: str, data):
    """! Get & Replace the stage template file and create a new one with stage_name
    @verbatim
    Args:
        stage_name : The stage name
        folder     : The destination folder for the new files
        workflow_name : Workflow name under which the stage will run
        data       : The template file
    @endverbatim
    """

    data = data.replace('generatedStageName', to_capitalize_no_underscore(stage_name))
    data = data.replace('generatedWFName', workflow_name)

    create_file(folder + "/main.py", data)
    create_empty_init_file(folder)


def create_empty_init_file(folder: str):
    """Creates an empty __init__.py file
    Args:
        folder       : The folder we want to create the new file in.
    """

    new_init_file = folder + "/__init__.py"
    create_init_file(new_init_file, '')


def create_predictable_file(fileName):
    pass


def create_file(new_file_path, data):
    """! Create new file and write the data file into it
    @verbatim
    Args:
        new_file_path : New file name path.
        data          : The content of the new file.
    @endverbatim
    """

    if not os.path.exists(new_file_path):
        f = open(new_file_path, "w")
        f.write(data)
        f.close()


def create_init_file(init_path, init_export):
    """! if init file doesn't exist - create it and add the export line
         if init file exist - check if the init_export line appears in the init file : if not add it.

    @verbatim
    Args:
        init_path   : Init file.
        init_export : Import line to add if needed.
    @endverbatim
    """

    if not os.path.exists(init_path):
        f = open(init_path, "w")
        f.write(init_export)
        f.close()
    else:
        f = open(init_path, 'r+')
        data = f.read()
        if init_export not in data:
            if len(data) and not data.endswith('\n'):
                f.write('\n')
            f.write(init_export)
            f.close()


def save_file(file_name_path, data):
    f = open(file_name_path, "w")
    f.write(data)
    f.close()


def inject_to_pipeline(fileName, type, className, new_init_export):
    """! Building the component in the pipeline file
    @verbatim
    Args:
        fileName       : New file name.
        type           : New component type (forcer or predictable)
        className      : New component class.
        new_init_export: Create init file - if doesnt exist.
    @endverbatim
    """

    file_path = 'pipeline/pipeline.py'
    if os.path.exists(file_path):
        data = read_file(file_path)
        new_tab_line = '\n'
        data_changed = False
        last_index_of_import = -1
        first_index_of_add_component = -1
        index_of_class = re.search(r'class[^\n]*', data)

        # finding current indent config
        index_of_build_pipeline = re.search(r'def build_pipeline[^\n]*', data)
        index_of_build_preprocessor = re.search(r'self.preprocessor =[^\n]*', data)
        index_of_build_postprocessor = re.search(r'self.postprocessor =[^\n]*', data)
        index_of_build_pipeline_row = re.search(r'.*def build_pipeline[^\n]*', data)
        if index_of_build_pipeline:
            build_pipeline_indent = (index_of_build_pipeline.start() - index_of_build_pipeline_row.start()) * 2
            new_tab_line = new_tab_line.ljust(build_pipeline_indent + 1)

        attr = fileName + type.title()
        new_component_line = 'self.' + attr + ' = ' + className + '()'
        add_component_line = 'self.add_component(self.' + attr + ')'

        # finding imports and add components indexes
        last_index_of_add_component = -1
        all_from_import = [i.end() for i in re.finditer(r'from[^\n]*', data)]
        all_add_components = [[i.start(), i.end()] for i in re.finditer(r'self.add_component[^\n]*', data)]
        if len(all_from_import):
            last_index_of_import = all_from_import[-1]
        if len(all_add_components):
            first_index_of_add_component = all_add_components[0][0]
            last_index_of_add_component = all_add_components[-1][-1]
        # finding imports and add components indexes

        index_to_add = 0

        # add import to end of imports or to top of file
        if last_index_of_import > -1 and new_init_export not in data:
            s = '\n' + new_init_export
            index_to_add += len(s)
            data = data[:last_index_of_import] + s + data[last_index_of_import:]
            data_changed = True
        elif index_of_class and new_init_export not in data:
            s = new_init_export + '\n\n'
            index_to_add += len(s)
            data = data[:index_of_class.start()] + s + data[index_of_class.start():]
            data_changed = True

        # check if build_pipeline exist but with no components yet
        if first_index_of_add_component == -1 and last_index_of_add_component == -1 and index_of_build_pipeline:
            s = new_tab_line
            current_end = index_of_build_pipeline.end()
            if index_of_build_preprocessor:
                current_end = index_of_build_preprocessor.end()
            if index_of_build_postprocessor:
                current_end = index_of_build_postprocessor.end()
            index = current_end + index_to_add
            index_to_add += len(s)
            data = data[:index] + s + data[index:]
            data_changed = True
            first_index_of_add_component = current_end
            last_index_of_add_component = current_end

        # adding new component line
        if first_index_of_add_component > -1 and new_component_line not in data:
            first_index_of_add_component += index_to_add
            if len(all_add_components):
                new_component_line = new_component_line + new_tab_line
            index_to_add += len(new_component_line)
            data = data[:first_index_of_add_component] + new_component_line + data[first_index_of_add_component:]
            data_changed = True

        # adding add_component line
        if last_index_of_add_component > -1 and add_component_line not in data:
            last_index_of_add_component += index_to_add
            add_component_line = new_tab_line + add_component_line
            index_to_add += len(add_component_line)
            data = data[:last_index_of_add_component] + add_component_line + data[last_index_of_add_component:]
            data_changed = True

        if data_changed:
            write_to_file(file_path, data)


def create_project_config_yaml():
    """! Creates /pipeline/config.yaml from dsframework/cli/config.yaml """
    with open(os.path.join(__location__, 'dsframework/cli/config.yaml'), 'r') as file:
        data = file.read()
        data = data.replace('generatedDirectory', directories['main'])
        new_file = directories['main'] + '/pipeline/config.yaml'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()


def create_project_config_json():
    """! Creates /config/config.json from dsframework/cli/config.json """
    with open(os.path.join(__location__, 'dsframework/cli/config.json'), 'r') as file:
        data = file.read()
        data = data.replace('generatedDirectory', directories['main'])
        new_file = directories['main'] + '/config/config.json'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()


def create_project_gitignore():
    """! Creates /.gitignore from dsframework/cli/.gitignore
         Which means all files that appear in the project directory and should not be uploaded to the git repository.
    """
    with open(os.path.join(__location__, 'dsframework/cli/.gitignore'), 'r') as file:
        data = file.read()
        new_file = directories['main'] + '/.gitignore'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()


def create_server_config_json():
    """! Creates server/cors_allowed_origins from dsframework/cli/cors_allowed_origins   """
    with open(os.path.join(__location__, 'dsframework/cli/cors_allowed_origins.json'), 'r') as file:
        data = file.read()
        data = data.replace('generatedDirectory', directories['main'])
        new_file = directories['server'] + '/cors_allowed_origins.json'
        if not os.path.exists(new_file):
            f = open(new_file, "w")
            f.write(data)
            f.close()


def change_to_project_dir():
    """! Change the OS dir path """
    os.chdir(directories['main'])


def run_dvc_init():
    """! Running dvc init and doing the following:
    1. Defines where all the dvc will be uploaded (DVC_BUCKET=)
    2. dvc init    - generate a local repository
    3. dvc config
    4. dvc remote add - connect my local repo -> remote
    5. dvc remote modify
    """
    dir_path = os.getcwd()
    if not os.path.isdir(dir_path + '/.dvc'):
        command = 'dvc_init.sh'
        if not isWindows:
            command = './' + command
        subprocess.call(command, shell=True)


def run_git_init():
    """! Using git_init.sh to create a new project on git
        https://git.zoominfo.com/dozi/{name-your-service}
    """
    dir_path = os.getcwd()
    if not os.path.isdir(dir_path + '/.git'):
        command = 'git_init.sh'
        if not isWindows:
            command = './' + command
        subprocess.call(command, shell=True)


def copy_logger_files(project_name):

    source_dir = os.path.join(__location__, 'dsframework/cli/logger/')
    target_dir = os.path.join(os.path.abspath(os.getcwd()), project_name, 'logger')
    if not os.path.exists(target_dir):
        shutil.copytree(source_dir, target_dir)


def copy_deploy_files(main_dir):
    """! Copy deploy files (from dsframework/cli/tester/deploy_files """
    currentPipelineFolder = os.path.basename(os.getcwd())
    if main_dir:
        currentPipelineFolder = main_dir
    dir = os.path.join(__location__, 'dsframework/cli/tester/deploy_files/')
    listOfFiles = list()
    for (dirpath, dirname, filenames) in os.walk(dir):
        dirpath = dirpath.replace(dir, '')
        listOfFiles = [os.path.join(dirpath, file) for file in filenames]
        for file_path in listOfFiles:
            with open(os.path.join(dir, file_path), 'r', encoding="utf8") as file:
                try:
                    data = file.read()
                    data = data.replace('{name-your-service}', currentPipelineFolder)
                    data = data.replace('{name-your-artifacts}', currentPipelineFolder)
                    dirToCreate = ''
                    if main_dir:
                        dirToCreate = os.path.join(main_dir, dirpath)
                    if not os.path.exists(dirToCreate):
                        os.makedirs(dirToCreate)
                    if not os.path.exists(os.path.join(main_dir, file_path)):
                        f = open(os.path.join(main_dir, file_path), "w")
                        f.write(data)
                        f.close()
                        # Make sure that .sh files can be executed
                        if (os.path.join(main_dir, file_path)).endswith('.sh'):
                            os.chmod(dirToCreate + file_path, 0o744)
                except Exception as ex:
                    pass


def copy_cloud_eval_files(main_dir):
    """! Copy cloud evaluation files """
    currentPipelineFolder = os.path.basename(os.getcwd())
    if main_dir:
        currentPipelineFolder = main_dir
    service_folder = str(currentPipelineFolder)
    service_name = service_folder.split('/')[-1]
    project_name_no_underscore = clean_existing_project_name(service_name)
    cloud_eval_dir = os.path.join(__location__, 'dsframework/cli/tester/cloud_eval/')
    listOfFiles = list()
    conflicted_files = []
    for (dirpath, dirname, filenames) in os.walk(cloud_eval_dir):
        if "__pycache__" in dirpath:
            continue
        dirpath = dirpath.replace(cloud_eval_dir, '')
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
        for file_path in listOfFiles:
            framework_source_file = os.path.join(cloud_eval_dir, file_path)
            with open(framework_source_file, 'r', encoding="utf8") as file:
                try:
                    data = file.read()
                    data = data.replace('{name-your-service}', service_name)
                    data = data.replace('{name-your-artifacts}', service_name)
                    data = data.replace('generatedProjectName', project_name_no_underscore)
                    dirToCreate = ''
                    if main_dir:
                        dirToCreate = main_dir + '/cloud_eval/'
                    if not os.path.exists(dirToCreate):
                        os.makedirs(dirToCreate)
                    if "#cli_file_dest=[" in data:
                        start_ix = data.index("#cli_file_dest=[") + len("#cli_file_dest=[")
                        end_ix = data.index("]", start_ix)
                        destination_dir = data[start_ix:end_ix]
                        data = data[:data.index("#cli_file_dest=[")] + data[end_ix + 1:]
                        dirToCreate = main_dir + '/' + destination_dir

                    if not os.path.exists(dirToCreate + file_path):
                        f = open(dirToCreate + file_path, "w")
                        f.write(data)
                        f.close()
                        # Make sure that .sh files can be executed
                        if (dirToCreate + file_path).endswith('.sh'):
                            os.chmod(dirToCreate + file_path, 0o744)
                    else:
                        with open(dirToCreate + file_path, "r") as f:
                            existing_data = f.read()
                        if existing_data != data:
                            conflicted_file = f"{dirToCreate + file_path}"
                            conflicted_files.append((conflicted_file, str(framework_source_file)))

                except Exception as ex:
                    pass

    if conflicted_files:
        print("The following files already exists, so not overwriting them. "
              "However, notice it is different from the framework version in")
        for conflicted_file in conflicted_files:
            print(f"Existing: [{conflicted_file[0]}] \t\t Framework source file [{conflicted_file[1]}]")


def copy_batch_files(main_dir):
    """! Generate batch files needed for batch projects.
        Args:
            main_dir: A string describing the main working directory, on existing projects, it's empty.
    """

    current_folder = os.path.basename(os.getcwd())
    if main_dir != '':
        current_folder = main_dir
    service_name = current_folder.split('/')[-1]
    project_name_no_underscore = clean_existing_project_name(service_name)
    source_dir = os.path.join(__location__, 'dsframework/cli/tester/batch_files/')

    for (dir_path, dir_name, filenames) in os.walk(source_dir):
        if "__pycache__" in dir_path:
            continue

        dir_path = dir_path.replace(source_dir, '')
        file_list = [os.path.join(dir_path, file) for file in filenames]
        for file_path in file_list:
            file_suffix = Path(file_path).suffix
            with open(os.path.join(source_dir, file_path), 'r', encoding="utf8") as file:
                try:
                    data = file.read()
                    data = data.replace('{name-your-service}', service_name)
                    data = data.replace('generatedProjectName', project_name_no_underscore)

                    if main_dir == '':
                        target_dir = 'batch_files/'
                        dir_to_create = target_dir
                    else:
                        target_dir = current_folder + '/batch_files/'
                        dir_to_create = target_dir

                    if dir_path != "":
                        dir_to_create = target_dir + dir_path + '/'

                    if not os.path.exists(dir_to_create):
                        os.makedirs(dir_to_create)
                    if not os.path.exists(target_dir + file_path):
                        f = open(target_dir + file_path, "w")
                        f.write(data)
                        f.close()
                        if file_suffix == '.sh':
                            os.chmod(target_dir + file_path, 0o744)
                except Exception as ex:
                    if file_suffix == '.jar':
                        shutil.copy(os.path.join(source_dir, file_path), f'{dir_to_create}')
                    else:
                        print(f'Error when trying to open: {file_path}: {ex}')
                    pass


def copy_trainer_files():
    """! This function will create a trainer environment."""

    project_name = os.getcwd().split('/')[-1]
    trainer_main_folder = 'trainer/'
    trainer_plwrapper_folder = 'trainer/pl_wrapper/'

    trainer_file_list = ["trainer/pl_wrapper/custom_dataset",
                         "trainer/pl_wrapper/data_module",
                         "trainer/pl_wrapper/iterable_dataset",
                         "trainer/pl_wrapper/network_module",
                         "trainer/pl_wrapper/plmodel",
                         "trainer/comparison",
                         "trainer/config",
                         "trainer/data",
                         "trainer/dataset_preparation",
                         "trainer/main",
                         "trainer/model",
                         "trainer/test",
                         "trainer/train"]

    if not os.path.exists(trainer_main_folder):
        os.mkdir(trainer_main_folder)

    if not os.path.exists(trainer_plwrapper_folder):
        os.mkdir(trainer_plwrapper_folder)

    for filename_path in trainer_file_list:
        file_only = filename_path.split('/')[-1]
        parent_folder = filename_path.split('/')[-2]

        dst_folder = ''
        if parent_folder == 'pl_wrapper':
            dst_folder = trainer_plwrapper_folder

        data = read_template_file(filename_path)

        clean_project_name = clean_existing_project_name(project_name)
        filename_no_underscore = to_capitalize_no_underscore(file_only)

        class_name = clean_project_name + filename_no_underscore

        data = data.replace('generatedClass', class_name)
        data = data.replace('generatedProjectName', clean_project_name)

        new_file = trainer_main_folder + file_only + ".py"
        if dst_folder != '':
            new_file = dst_folder + file_only + ".py"

        if not os.path.isfile(new_file):
            create_file(new_file, data)
        else:
            print(f'File \'{new_file}\' exists, skipping.')

    source_path = os.path.join(__location__, 'dsframework/cli/', 'trainer/requirements_trainer.txt')
    shutil.copyfile(source_path, trainer_main_folder + '/requirements_trainer.txt')

    print("Creating trainer environment done !")


def copy_documentation_files(target_dir):
    """! Copy documentation folder to newly created project.

    Args:
        target_dir: Newly created project location
    """
    source_dir = os.path.join(__location__, 'dsframework/documentation/')
    if not os.path.exists(target_dir):
        shutil.copytree(source_dir, target_dir, ignore=shutil.ignore_patterns('dsf_doxy*'))


def update_doc_configuration(project_name, target_dir):
    """! Update project doxygen configuration file, adding project name.

    Args:
        project_name: Newly created project name
        target_dir: Configuration file location.
    """
    project_name_no_underscore = to_capitalize_no_underscore(project_name)
    source_dir = os.path.join(target_dir, 'project_doxyfile')
    data = read_file(source_dir)
    data = data.replace('generatedProjectName', project_name_no_underscore)
    save_file(source_dir, data)


@cli.command()
def install_trainer_packages():
    """! Install trainer packages."""
    command = 'pip install -r trainer/requirements_trainer.txt'
    subprocess.call(command, shell=True)


@cli.command()
def install_documentation_requirements():
    """! Install documentation doxygen."""

    doxygen_found = True

    try:  # Check for brew installation
        command = 'brew -v'
        res = subprocess.check_output(command, shell=True)
        brew_found = 'Homebrew' in str(res)

        if brew_found:
            try:  # Check for doxygen installation (if brew found)
                command = 'brew ls --versions doxygen'
                res = subprocess.check_output(command, shell=True)
                doxygen_found = 'doxygen' in str(res)

                if doxygen_found:
                    print('Doxygen already installed.')

            except subprocess.CalledProcessError as e1:
                doxygen_found = False

    except subprocess.CalledProcessError as e2:
        brew_found = False

    if not doxygen_found or not brew_found:
        installation_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dsframework', 'documentation',
                                         'install_doxygen.sh')
        if not os.path.exists(installation_file):
            print('Installation script not found install_doxygen.sh')
            return
        is_mac_linux = (platform.system() == 'Darwin' or platform.system() == 'Linux')

        if is_mac_linux:
            subprocess.call(f'chmod +x {installation_file}', shell=True)

        subprocess.call(installation_file, shell=True)


def to_capitalize_no_underscore(text):
    """! Capitalize each word with no underscore
     for example : Moving from test_name -> TestName"""
    return ''.join(elem.capitalize() for elem in text.split('_'))


def clean_existing_project_name(text):
    no_underscore_text = to_capitalize_no_underscore(text)
    return ''.join(elem.capitalize() for elem in no_underscore_text.split('-'))


def let_user_pick(options):
    """! Let the user pick a number from couple of options
    @verbatim
    Args:
        options  : couple of options for user decision.
    @endverbatim
    """
    print("Please choose:")
    for idx, element in enumerate(options):
        print("{}) {}".format(idx + 1, element))
    i = input("Enter number: ")
    try:
        if 0 < int(i) <= len(options):
            return int(i) - 1
    except:
        pass
    return None


@cli.command()
def deploy_service_to_gae():
    """! Run deployment scripts in order to deploy the current project to GAE.
   """
    # Setup paths to script files
    setup_file_path = f"{__proj_root__}/deploy/setup_deploy_params.sh"
    framework_folder = os.path.dirname(os.path.abspath(__file__))

    # Check that we have a setup file. If not, copy it.
    if not os.path.exists(setup_file_path):
        print(f"file {setup_file_path} doesn't exist. Copying. Please fill relevant parameters and run again")
        shutil.copyfile(f"{framework_folder}/dsframework/cli/tester/deploy_files/deploy/setup_deploy_params.sh",
                        setup_file_path)
        return

    # Prepare commands
    setup_command = f"source {setup_file_path}"
    build_command = f"{framework_folder}/dsframework/base/deploy_scripts/build_and_register_image_in_devland.sh"
    deploy_command = f"{framework_folder}/dsframework/base/deploy_scripts/gae/deploy-gae-devland.sh"
    full_command = f"{setup_command};{build_command};{deploy_command}"

    # Execute
    subprocess.call(full_command, shell=True)
    # subprocess.call(setup_command, shell=True)
    # subprocess.call(build_command, shell=True)
    # subprocess.call(deploy_command, shell=True)


if __name__ == '__main__':
    cli(prog_name='cli')

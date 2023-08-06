from cookiecutter.main import cookiecutter
import plumbum.cli
from plumbum import local
import requests
from collections import ChainMap, namedtuple
import cortex_cli.cli.api.github_api as gh

import conda_pack
import traceback
import os
import os.path
import mlflow
import yaml
import sys
from tqdm import tqdm
import os, shutil
import importlib
from datetime import datetime
from mlflow.models.signature import infer_signature
from os import walk

from cortex_cli.cli.cli_api_base import CliApiBase
from cortex_cli.cli.cli_multipart_upload import MultipartUpload

import cortex_cli.core.mlflow.mlflow_cortex as mlflow_cortex
from cortex_cli.core.ethics_checks import EthicsResult
from cortex_cli.core.drift_checks import DriftResult
from cortex_cli import __version__


class ModelsCli(plumbum.cli.Application):
    NAME = 'models'


@ModelsCli.subcommand('init')
class InitModel(CliApiBase):
    MODEL_TEMPLATES_PATH = 'model_templates'
    MODEL_TEMPLATES = [
        'digits_model',
        'chatgpt_model'
    ]


    _name = plumbum.cli.SwitchAttr(
        names=['-n', '--name'],
        argtype=str,
        help='The name of the model. Should use a readable format, ie. Digits Model',
        default=None
    )

    _repo = plumbum.cli.SwitchAttr(
        names=['-r', '--repo'],
        argtype=str,
        help='The name of the repository. Should use dash case, ie. digits-model',
        mandatory=True
    )

    _description = plumbum.cli.SwitchAttr(
        names=['-d', '--description'],
        argtype=str,
        default='A model that is initialized through the Cortex CLI.',
        help='A description of the model'
    )

    _template = plumbum.cli.SwitchAttr(
        names=['-t', '--template'],
        argtype=str,
        default='digits_model',
        help='The template to use for the model. The default is "digits_model".\nAvailable choices are: ' + ', '.join(MODEL_TEMPLATES),
    )

    _token = plumbum.cli.SwitchAttr(
        names=['--github-token'],
        argtype=str,
        envname='GH_TOKEN'
    )

    _org = plumbum.cli.SwitchAttr(
        names=['--github-org'],
        argtype=str,
        envname='GH_ORG',
        default='nearlyhuman'
    )

    _path = plumbum.cli.SwitchAttr(
        names=['-p', '--path'],
        argtype=str,
        envname='MODEL_PATH',
        default='.'
    )

    _register = plumbum.cli.Flag(
        names=["--register"],
        default=True
    )

    # Properties

    @property
    def _template_location(self):
        current = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(current, self.MODEL_TEMPLATES_PATH)
        return os.path.join(template_path, self._template)

    @property
    def _model_path(self):
        return os.path.join(self._path, self._repo)


    def main(self, *args):
        self._error_message = None

        # Instantiate the model name if it hasn't been set.
        if not self._name:
            self._name = self._repo.replace('-', ' ').title()

        github = gh.Github(
            self._repo,
            self._description,
            # TODO: Need to separate out this organization because the GH account can be from anywhere.
            self._org,
            self._token
        )

        try:
            self._validate_repo()
            self._generate_template_repo()

            # Create the repository in Github
            self._create_repo(github)

            # Register the model with Cortex
            self._register_model()
        except Exception as e:
            self._fail(e)
            self._error_message = e
        finally:
            if not self._error_message:
                self._pass(f'Successfully generated the model repository at "{self._model_path}"')
        return


    def _validate_repo(self):
        if os.path.exists(self._model_path):
            raise Exception(f'The directory "{self._model_path}" already exists. Either rename the directory or register the repository directly.')


    def _generate_template_repo(self):
        cookiecutter(
            self._template_location,
            no_input=True,
            output_dir=self._path,
            extra_context={
                'model_name': self._name,
                'model_repo': self._repo,
                'description': self._description,
                'version': __version__
            }
        )


    def _create_repo(self, github):
        if self._token:
            try:
                # Create the repository in Github
                response = self._handle_api_response(gh.create_repo(github))

                # Commit and push to the new repo in Github
                repo = gh.Repo(path=self._model_path)
                repo.init() \
                    .set_remote(github.owner, github.repo_name) \
                    .add() \
                    .commit('Initial commit. Generated from Cortex CLI using the model template.') \
                    .push()

                self._pass(
                    f'Created the GitHub repository "{self._org}/{self._repo}"')
                return response
            except Exception as e:
                raise Exception(f'An error occurred while initializing the GitHub repo.\n{e}')


    def _register_model(self):
        if self._register:
            response = requests.post(
                url=self._endpoint,
                headers=self._headers,
                json={
                    'name': self._name,
                    'repo': self._repo,
                    'githubEnabled': True if self._token else False
                }
            )

            self._handle_api_response(
                response, f'Registered the model repository {response.json()["_id"]}')


@ModelsCli.subcommand('register')
class RegisterModel(CliApiBase):
    _repo = plumbum.cli.SwitchAttr(
        names=['-r', '--repo'],
        argtype=str,
        mandatory=True
    )

    _name = plumbum.cli.SwitchAttr(
        names=['-n', '--name'],
        argtype=str,
        mandatory=True
    )


    def main(self, *args):
        try:
            response = self._register_model()
            self._print(response)
        except Exception as e:
            self._fail(e)


    def _register_model(self):
        return self._handle_api_response(requests.post(
            url=self._endpoint,
            headers=self._headers,
            json={
                'name': self._name,
                'repo': self._repo,
                'githubEnabled': True if gh.Repo().hash else False
            }
        ))


@ModelsCli.subcommand('run')
class RunModelPipeline(CliApiBase):
    _path = plumbum.cli.SwitchAttr(
        names=['-p', '--path'],
        argtype=str,
        envname='MODEL_PATH',
        default='.'
    )

    _tracking = plumbum.cli.Flag(
        names=['-t', '--tracking'],
        default=True
    )

    _running_pipeline_id = plumbum.cli.SwitchAttr(
        names=['-i', '--pipeline-id'],
        argtype=str,
        envname='NH_PIPELINE_ID',
        default='current_running_pipeline_id'
    )

    _cortex_env_path = plumbum.cli.SwitchAttr(
        names=['-e', '--env'],
        argtype=str,
        envname='CORTEX_ENV_PATH',
        default=None
    )

    # Properties

    @property
    def _model_id(self):
        return self._model_json['_id'] if self._model_json else None

    @property
    def _pipeline_id(self):
        return self._pipeline_json['_id'] if self._pipeline_json else None

    modules = {}
    @property
    def _modules(self):
        if self.modules:
            return self.modules
        for (root, dir_names, file_names) in walk(self._config['module_path']):
            file_names[:] = [
                f for f in file_names 
                if f.endswith('.py') and f not in ['__init__.py', '{}.py'.format(self._config['model_module'])] 
            ]
            # TODO: Set map of file path locations to module name
            for f in file_names:
                self.modules['{}/{}'.format(root, f)] = f.replace('.py', '')
        return self.modules

    @property
    def _model_module(self):
        return '{}/{}.py'.format(self._config['module_path'], self._config['model_module'])
    
    @property
    def _model_dir(self):
        return self._config['module_path']
    
    @property
    def _artifacts_dir(self):
        location = 'cortex' if self._tracking else 'local'
        id = self._pipeline_id if self._tracking and self._pipeline_id else self._now
        return f'models/{location}/{id}'
    
    @property
    def _pipeline_steps(self):
        Step = namedtuple('Step', 'name type')
        return [Step(dict[list(dict.keys())[0]], list(dict.keys())[0]) for dict in self._config['pipeline_steps']]

    _now = datetime.now().strftime('%m%d%Y-%H%M%S')

    @property
    def _config(self):
        return self._read_yaml('cortex.yml')

    # Helpers

    def _load_module(self, module_path, module_name):
        print('\t\tLoading module {} from {}'.format(module_name, module_path))
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


    def _read_yaml(self, file: str) -> dict:
        if not os.path.exists(file):
            self._fail(f'Error! No "{file}" found in this Model project.')

        with open(file, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)

# -------------------------------------------------------------------------------

    def main(self, *args):
        # Change to working directory
        os.chdir(self._path)

        self.model = None
        self._error_message = None
        self._success = False
        self._model_json = None
        self._pipeline_json = None
        self._requested_secrets = []
        try:
            self._model_json = self._get_model()
            # Step 1 - Get live model data
            if self._tracking:
                self._mlflow_client = self._setup_mlflow()
                self._setup_pipeline()

            # Step 2 - Load the Model Class
            self.model = self._instantiate_model()

            # Step 3 - Initialize the pipeline steps
            self._initialize_steps()

            # Step 4 - Run the pipeline
            if self._tracking:
                self._pipeline_json = self._run_pipeline()

            # Step 5 - Run the pipeline steps
            self._run_pipeline_steps()
        except Exception as e:
            if not self._error_message:
                self._error_message = traceback.format_exc()
        finally:

            try:
                # Step 9 - Contact callback route to update currentStage of model pipeline
                if self._tracking and self._pipeline_json and self._model_json:
                    status = 'Failed' if self._error_message or not self._success else 'Successful'
                    self._complete_callback(
                        status,
                        self._error_message
                    )
            except Exception as e:
                self._fail(f'An internal server error has occurred!\n{e}')

            if self._error_message:
                self._fail(self._error_message)
            else:
                self._pass('Completed Cortex Pipeline Run')

# -------------------------------------------------------------------------------

    def _initialize_steps(self):
        # Convert yaml steps to ml-api format
        _steps = []

        # Add default download data step
        _steps.append({
            'name':   'Download data',
            'type':   'download_data',
            'config': {}
        })

        for step in self._pipeline_steps:
            _steps.append({
                'name':   step.name,
                'type':   step.type,
                'config': {}
            })
        
        # Add default download data step
        _steps.append({
            'name':   'Cleanup model params',
            'type':   'cleanup_self',
            'config': {}
        })

        # Add default save pipeline artifacts step
        _steps.append({
            'name':   'Save pipeline artifacts',
            'type':   '_save_pipeline',
            'config': {
                'cortex_cli_func': True
            }
        })

        # Add default save pipeline environment step
        _steps.append({
            'name':   'Save pipeline environment',
            'type':   '_save_environment',
            'config': {
                'cortex_cli_func': True
            }
        })

        # Add default upload to cortex step
        _steps.append({
            'name':   'Upload pipeline artifacts',
            'type':   '_upload_pipeline',
            'config': {
                'cortex_cli_func': True,
                'requires_tracking': True
            }
        })
        
        if self._tracking:
            # Set cortex steps
            self._steps = self._create_steps(_steps)
        else:
            # Set normal steps
            self._steps = _steps

        self._pass('Loaded pipeline steps')


    def _create_steps(self, _steps):
        response = requests.post(
            url=f'{self._api_url}/pipelines/{self._pipeline_id}/steps',
            headers=self._headers,
            json={
                'stepsConfig': _steps
            }
        ).json()

        if len(response) == 0:
            raise Exception('Error! Failed to load the pipeline steps.')
        
        return response


    def _complete_step(self, step, step_status, step_result, step_risk):
        json_value = None

        # Setup json value depending on if we have risk or not
        json_value = {
            'pipelineId':    step['pipelineId'],
            'name':          step['name'],
            'type':          step['type'],
            'order':         step['order'],
            'status':        step_status,
            'statusMessage': '' if step_result is None else str(step_result)
        }

        if step_risk != '':
            json_value['risk'] = step_risk

        return requests.put(
            url=f'{self._api_url}/steps/{step["_id"]}/complete',
            headers=self._headers,
            json=json_value
        ).json()


    def _get_drift_inferences(self):
        response = requests.get(
            url=f'{self._api_url}/inferences?modelId={self._model_id}&hasTags[]=Drift Detection',
            headers=self._headers
        ).json()

        inferences = []
        if response and len(response['documents']) > 0:
            for inference in response['documents']:
                if inference['successful']:
                    inferences.append((inference['_id'], [inference['inputs']['ndarray'][0]], [inference['outputs']['ndarray'][0]]))

        return inferences

# -------------------------------------------------------------------------------

    def _get_pipeline(self, git_branch, model_id):
        query = {
            'cloud':     True
        }

        response = requests.get(
            url=f'{self._api_url}/pipelines/{self._running_pipeline_id}',
            params=query,
            headers=self._headers,
            json={'modelId': model_id}
        )

        pipeline = response.json()
        
        if ('statusCode' in pipeline and pipeline['statusCode'] != 200) or ('currentStage' in pipeline and pipeline['currentStage'] != 'Pending'):
            self._pass(f'Did not find existing pipeline for branch {git_branch}')
            return None
        
        message = f'Found existing pipeline {pipeline["_id"]} for branch {git_branch} with status {pipeline["currentStage"]}.'

        if pipeline['currentStage'] == 'Running':
            raise Exception(
                f'{message} The cloud initiated training needs to complete first on this branch before running again.')

        if pipeline['currentStage'] == 'Pending':
            self._pass(message)
            return pipeline
        
        return None


    def _create_pipeline(self, model_id, git_branch, git_hash):
        response = requests.post(
            url=f'{self._api_url}/pipelines',
            headers=self._headers,
            json={
                'modelId':   model_id,
                'gitBranch': git_branch,
                'gitHash':   git_hash
            }
        ).json()
        
        return response


    def _run_pipeline(self):
        return requests.put(
            url=f'{self._api_url}/pipelines/{self._pipeline_id}/run',
            headers=self._headers,
            json={
                'modelId': self._model_id
            }
        ).json()


    def _run_pipeline_steps(self):
        current_step = None
        try:
            for step in self._steps:
                current_step = step['type']
                step_config = step['config']
                step_func = getattr(self if step_config.get('cortex_cli_func') else self.model, current_step)
                step_result = None

                # Extract secrets from model if we are in cleanup step
                if current_step == 'cleanup_self':
                    self._requested_secrets = self.model.secrets_manager.secrets

                # Handle special case for passing testing inferences to test_predict function
                if current_step == 'detect_drift':
                    step_result = step_func(self._get_drift_inferences())
                else:
                    if (step_config.get('requires_tracking') and self._tracking) or (not step_config.get('requires_tracking')):
                        step_result = step_func()

                if self._tracking:
                    step_risk = ''

                    # Get ethics check results (if it exists)
                    if type(step_result) is EthicsResult:
                        # Parse out risk level
                        step_risk = step_result.risk.value

                        # Parse out result
                        step_result = step_result.result_str
                    elif type(step_result) is DriftResult:
                        # Parse out result
                        step_result = step_result.result_str

                    self._complete_step(step, 'Successful',
                                        step_result, step_risk)
                self._pass(
                    f'{step["name"]} completed successfully')
            self._success = True
        except Exception as e:
            if self._tracking:
                self._complete_step(step, 'Failed', str(e), '')
            self._error_message = f'{step["name"]} completed with an error.\n{traceback.format_exc()}'
            raise Exception


    def _setup_pipeline(self):
        pipeline_response = None

        # Get the local branch
        git_branch = gh.Repo().branch
        git_hash = gh.Repo().hash

        if (self._model_json['githubEnabled']):
            if git_hash is None or git_hash == '':
                self._fail('Could not get git commit hash. Please initialize the git repository and commit your code before running the pipeline.')

            # Look for an existing 'Pending' pipeline for this branch
            pipeline_response = self._get_pipeline(
                git_branch,
                self._model_id
            )

        if pipeline_response:
            self._pipeline_json = pipeline_response
            return

        # If not found, create the locally sourced pipeline
        self._pipeline_json = self._create_pipeline(
            self._model_id,
            git_branch,
            git_hash
        )

        self._pass(f'Pipeline {self._pipeline_json["currentStage"]} with id: {self._pipeline_id}')

# -------------------------------------------------------------------------------

    def _get_model(self):
        query = {
            'repo': self._config['model_repo']
        }

        response = requests.get(
            url=self._endpoint,
            params=query,
            headers=self._headers
        )

        if response.status_code != 200 or 'documents' not in response.json() or len(response.json()['documents']) != 1:
            raise Exception('Error! This model could not be found')
        
        model = response.json()['documents']

        self._pass(
            f'Found the model {self._config["model_repo"]}')

        return model[0]


    def _complete_callback(self, status, error_message=None):
        body = {
            'modelId':      self._model_id,
            'currentStage': status,
            'secrets': self._requested_secrets
        }

        if error_message:
            body['message']: error_message

        requests.put(
            url=f'{self._api_url}/pipelines/{self._pipeline_id}/run/complete',
            headers=self._headers,
            json=body
        )


    def _save_pipeline(self):
        self._info('Saving pipeline artifacts...')
        signature = infer_signature(self.model.input_example, self.model.output_example)

        # Save model
        modules = list(self._modules.keys())
        modules.append(self._model_module)
        if self.model.model_type == 'cortex':
            mlflow_cortex.save_model(
                python_model=self.model, 
                path=self._artifacts_dir,                   # Where artifacts are stored locally
                code_path=list(modules),                    # Local code paths not on
                conda_env='conda.yml',
                artifacts={},
                custom_objects=self.model.custom_objects,
                signature=signature
            )
        else:
            self._error_message = f"An error occurred while detecting the Cortex model type. \
            Found '{self.model.model_type}', but only ['cortex'] are acceptable values"
            raise Exception

        return f'Saved the pipeline artifacts to disk: ({self._artifacts_dir})'


    def _save_environment(self):
        self._info('Packing conda environment...')

        conda_pack.pack(
            prefix=self._cortex_env_path,
            output=f'{self._artifacts_dir}/environment.tar.gz',
            force=True,
            verbose=True,
            ignore_editable_packages=False,
            ignore_missing_files=True
        )

        return f'Packed conda environment to disk: ({self._artifacts_dir})'


    def _upload_pipeline(self):
        self._info('Uploading pipeline artifacts to Cortex...')

        file_paths = []

        # Get files from pipeline run
        for root, dirs, files in os.walk(self._artifacts_dir):
            for file in files:
                file_paths.append(os.path.join(root, file))

        for i in tqdm(range(len(file_paths))):
            uploadable_file = MultipartUpload(
                path = file_paths[i], 
                endpoint = f'{self._api_url}/pipelines/{self._pipeline_id}/files/multipart',
                headers = self._headers
            )
            
            uploadable_file.upload()
        
        return f'Uploaded the pipeline artifacts to Cortex'


    def _instantiate_model(self):
        # LOAD DEPENDENCY MODULES (except model)
        for path, module in self._modules.items():
            self._load_module(path, module)

        # LOAD MODEL MODULE
        model_module = self._load_module(
            '{}/{}.py'.format(self._config['module_path'], self._config['model_module']),
            self._config['model_module']
        )

        model_params = dict(ChainMap(*self._config['params'])) if self._config['params'] else {}
        return getattr(model_module, self._config['model_class'])(model_params, self._model_id, self._api_url, self._headers)


    def _setup_mlflow(self):
        # Create a client to make API calls to the tracking server
        return mlflow.tracking.MlflowClient()

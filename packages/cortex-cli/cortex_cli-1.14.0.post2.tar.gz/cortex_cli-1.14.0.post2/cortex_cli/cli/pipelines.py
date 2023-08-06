import os
import plumbum.cli
from cortex_cli.cli.cli_api_base import CliApiBase
import requests
import mlflow
import traceback


class PipelinesCli(plumbum.cli.Application):
    NAME = 'pipelines'


class PipelinesBase(CliApiBase):
    def main(self, *args):
        args_list = self._check_args_not_empty(args)
        action    = args_list[0]
        tracking  = args_list[1]
        self._id  = path = args_list[2]
        self._error_message = None

        try:
            if tracking:
                response = self._get_pipeline()
                response = self._deploy_cortex(action, response['modelId'])
            else:
                self._deploy_local(action, path)
        except:
            if not self._error_message:
                self._error_message = traceback.format_exc()
        finally:
            if self._error_message:
                raise Exception(self._error_message)
            else:
                self._pass(f'Completed Cortex Pipeline {action.title()}ment')


    def _get_pipeline(self) -> dict:
        return self._handle_api_response(requests.get(
            url     = f'{self._endpoint}/{self._id}',
            headers = self._headers
        ))


    def _deploy_local(self, action: str, path: str):
        if action == 'deploy':
            try:
                # Load model to check if it is valid
                model = mlflow.pyfunc.load_model(path)
            except Exception as e:
                raise Exception(f'Error loading model from path {path}: {e}')


    def _deploy_cortex(self, action: str, model_id: str):

        response = requests.put(
            url     = f'{self._endpoint}/{self._id}/{action}',
            headers = self._headers,
            json    = {'modelId': model_id}
        )
        
        return self._handle_api_response(response, f'Deploying the Model from pipeline {self._id}')


@PipelinesCli.subcommand('deploy')
class PipelinesDeploy(PipelinesBase):
    _tracking = plumbum.cli.Flag(
        names=['-t', '--tracking']
    )

    _path = plumbum.cli.SwitchAttr(
        names     = ['-p','--path'], 
        argtype   = str
    )

    _id = plumbum.cli.SwitchAttr(
        names     = ['-i','--id']
    )


    def main(self, *args):
        if self._id and self._path:
            self._fail('Cannot specify both --id and --path')

        if self._id:
            return super().main('deploy', self._tracking, self._id)

        return super().main('deploy', self._tracking, self._path)

@PipelinesCli.subcommand('undeploy')
class PipelinesUndeploy(PipelinesBase):
    _tracking = plumbum.cli.Flag(
        names=['-t', '--tracking']
    )

    _path = plumbum.cli.SwitchAttr(
        names     = ['-p','--path'], 
        argtype   = str,
        mandatory = True
    )

    _id = plumbum.cli.SwitchAttr(
        names     = ['-i','--id']
    )


    def main(self, *args):
        if self._id and self._path:
            self._fail('Cannot specify both --id and --path')

        if self._id:
            return super().main('undeploy', self._tracking, self._id)

        self._fail('Cannot specify --path or --tracking when undeploying')

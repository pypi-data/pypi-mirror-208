import plumbum.cli
from cortex_cli.cli.cli_api_base import CliApiBase
import requests


class InferencesCli(plumbum.cli.Application):
    NAME = 'inferences'


@InferencesCli.subcommand('create')
class CreateInference(CliApiBase):
    _model_id = plumbum.cli.SwitchAttr(
        names=['-m', '--model-id'],
        argtype=str,
        mandatory=True
    )

    _pipeline_id = plumbum.cli.SwitchAttr(
        names=['-p', '--pipeline-id'],
        argtype=str,
        mandatory=True
    )

    def main(self, *args):
        self.check_args_not_empty(args)

        response = self._create(args)
        self.print(response)

    def _create(self, args: tuple):
        return self._handle_api_response(requests.post(
            url=self._endpoint,
            headers=self._headers,
            json={
                'modelId':    self._model_id,
                'pipelineId': self._pipeline_id,
                'inputs':     list(args)
            }
        ))

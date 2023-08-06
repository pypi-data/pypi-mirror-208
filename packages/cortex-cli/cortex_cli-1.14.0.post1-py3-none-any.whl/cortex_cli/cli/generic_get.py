from cortex_cli.cli.clients import ClientsCli
import plumbum.cli
from cortex_cli.cli.cli_api_base import CliApiBase
from cortex_cli.cli.inferences import InferencesCli
from cortex_cli.cli.models import ModelsCli
from cortex_cli.cli.pipelines import PipelinesCli
import requests


@ClientsCli.subcommand('list')   # Weird, but technically valid
@InferencesCli.subcommand('list')
@ModelsCli.subcommand('list')
@PipelinesCli.subcommand('list')
class GetCli(CliApiBase):
    _id = plumbum.cli.SwitchAttr(
        names=['-i', '--id'],
        argtype=str,
        help='The ID of the Cortex resource being queried.'
    )


    def main(self, *args):
        response = self._get()
        self._print(response)


    def _get(self):
        endpoint = f'{self._endpoint}/{self._id}' if self._id else self._endpoint
        response = self._handle_api_response(requests.get(
            url=endpoint, headers=self._headers), terminate=True)

        return response

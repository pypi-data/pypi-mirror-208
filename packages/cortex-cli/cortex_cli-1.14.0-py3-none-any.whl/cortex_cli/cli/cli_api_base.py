import sys
import pprint
import plumbum.cli
from plumbum import colors
from requests import Response
from cortex_cli.cli.cli_api_base_config import CliApiBaseConfig, Var


class CliApiBase(plumbum.cli.Application, CliApiBaseConfig):
    """
    Inheritable class for things that should be included in every command.
    """

    _profile_ = plumbum.cli.SwitchAttr(
        names=['--profile'],
        argtype=str,
        default='default'
    )

    _api_key_ = plumbum.cli.SwitchAttr(
        names=['--api-key'],
        argtype=str
    )

    _api_url_ = plumbum.cli.SwitchAttr(
        names=['--api-url'],
        argtype=str
    )


    @property
    def _profile(self) -> str:
        return self._get_var(Var.PROFILE, self._profile_, self._profile_)


    @property
    def _api_key(self) -> str:
        return self._get_var(Var.API_KEY, self._profile_, self._api_key_)


    @property
    def _api_url(self) -> str:
        return self._get_var(Var.API_URL, self._profile_, self._api_url_)


    @property
    def _resource(self) -> str:
        assert self.parent.NAME  # This is REQUIRED to be defined
        return self.parent.NAME


    @property
    def _endpoint(self) -> str:
        return f'{self._api_url}/{self._resource}'


    @property
    def _headers(self) -> dict:
        return {
            'Content-Type':  'application/json',
            'Authorization': f'Bearer {self._api_key}'
        }


    @staticmethod
    def _check_args_not_empty(*args) -> list:
        args_list = list(*args)
        if not args_list:
            raise Exception('Missing expected arguments/input.')

        return args_list


    @staticmethod
    def _print(obj: object):
        pprint.pprint(obj)
        pprint


    @staticmethod
    def _info(message: str):
        print('  ', (colors.rgb(192, 192, 192) & colors.bold)['>'], message)


    @staticmethod
    def _pass(message: str):
        print('  ', (colors.green & colors.bold)['+'], message)


    @staticmethod
    def _fail(message: str, sub_message=None, terminate=False):
        print('  ', (colors.red & colors.bold)['x'], message)
        if sub_message != None:
            print('     ', sub_message)

        if terminate:
            sys.exit(1)


    @staticmethod
    def _handle_api_response(response: Response, success_message=None, failure_message=None, terminate=False):
        if response.json().get('status')  == 'ERROR':
            message = failure_message if failure_message else response.json().get('message')
            CliApiBase._fail(message, terminate=terminate)

        if success_message:
            CliApiBase._pass(success_message)

        return response.json()

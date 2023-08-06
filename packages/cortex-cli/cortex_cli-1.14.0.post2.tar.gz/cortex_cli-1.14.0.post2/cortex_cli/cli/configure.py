import os
from configparser import ConfigParser
import plumbum.cli


# This deliberately doesn't inherit from the CliApiBase class
class ConfigureCli(plumbum.cli.Application):
    """
    Create a configuration file, storing commonly used information in a profile.
    """
    
    _profile = plumbum.cli.SwitchAttr(
        names=['-p', '--profile'],
        argtype=str,
        help='The profile to save the configuration under.',
        default=None
    )

    _api_url = plumbum.cli.SwitchAttr(
        names=['-u', '--api-url'],
        argtype=str,
        help='The Nearly Human Cortex API endpoint.',
        default=None
    )

    _api_key = plumbum.cli.SwitchAttr(
        names=['-k', '--api-key'],
        argtype=str,
        help='The Nearly Human Cortex API Key to use.',
        default=None
    )

    def main(self, *args):
        config = ConfigParser(default_section=None)

        path = os.path.expanduser('~/.nearlyhuman/config')

        # Try to load an existing configuration, effectively updating existing
        # configurations
        try:
            with open(path) as file:
                config.read_file(file)

        except FileNotFoundError:
            # Ok for now, file will be created later
            pass


        # Prompt whenever switches are not used
        if not self._profile:
            self._profile = plumbum.cli.terminal.prompt('Profile:', type=str, default='default')

        if not self._api_url:
            self._api_url = plumbum.cli.terminal.prompt('API Url:', type=str, default='https://api.nearlyhuman.ai')

        if not self._api_key:          
            self._api_key = plumbum.cli.terminal.prompt('API Key:', type=str, default='')


        config[self._profile] = {
            'api_url': self._api_url,
            'api_key': self._api_key
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as file:
            config.write(file)

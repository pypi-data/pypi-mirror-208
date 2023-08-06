from __future__ import annotations
from configparser import ConfigParser
import os


class Var():
    """
    Represents a "known" variable that the Cortex CLI cares about.
    """

    API_KEY = 'NH_API_KEY'
    API_URL = 'NH_API_URL'
    PROFILE = 'NH_PROFILE'


    @staticmethod
    def _as_short(var: Var) -> str:
        index = str(var).index('_')
        return var[index + 1:]


class CliApiBaseConfig():
    """
    Helper for dealing with configuration and variables.

    This provides the utilities for handling saved information.
    """

    def _get_var_from_env(self, var: Var) -> str | None:
        """
        Try to get a Cortex CLI variable from the environment.
        """
        return os.environ.get(var)


    def _get_var_from_config(self, var: Var, profile: str) -> str | None:
        """
        Try to get a Cortex CLI variable from the configuration file.
        """
        path = os.path.expanduser('~/.nearlyhuman/config')

        # Just need to care if it exists or not, anything else is probably
        # actually exceptional and should bubble up as a failure
        if not os.path.exists(path):
            return None

        # Config saves variable names in a different format:
        # "NH_API_KEY" -> "api_key"
        parser = ConfigParser()
        parser.read(path)
        return parser[profile].get(Var._as_short(var).lower())


    def _get_var(self, var: Var, profile: str, prefer: str = '') -> str:
        """
        Try to get a configuration variable based on the specified profile.

        This will attempt to grab a variable, in order of:
        - Environment variable
        - Configuration file

        If the 'prefer' parameter is truthy, that value will always be returned.
        This allows for a CLI switch to always win out over other options.
        """
        assert profile

        # Provide an early out if prefer is set - this lets you use a SwitchAttr
        # or similar as the prefered value. If it's true-ish, this will return
        # that value instead of doing a lookup. This provies a way for an
        # explict argument to always win.
        if prefer:
            return prefer

        # Return the first available variable
        function_pointers = [
            (self._get_var_from_env, {'var': var}),
            (self._get_var_from_config, {'var': var, 'profile': profile})
        ]

        for func in function_pointers:
            kargs = dict(func[1])
            value = func[0](**kargs)
            if value:
                return value

        # All attempts to find the variable have failed
        if not value:
            raise Exception(f'No viable value for {var._as_short()}.')

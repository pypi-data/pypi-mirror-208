import json
import os
import requests


class Secret():
    _name = None
    _value = None


    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        if self._value is None:
            self._value = os.environ[self._name]
            if self._value is None:
                raise Exception(f'The variable {self._name} is not set on Cortex or local environment variables.')
        return self._value


    def __init__(self, name, value):
        self._name = name
        self._value = value


class SecretsManager():
    _api_url = None
    _headers = None
    _secrets = []
    _deployment_secrets_path = '/mnt/secrets/all.json'


    @property
    def secrets(self):
        """
        Returns: (list) List of secret names
        """
        return [ x.name for x in self._secrets ]


    def __init__(self, api_url, headers):
        self._api_url = api_url
        self._headers = headers


    def cache_secrets(self):
        """
        Caches secrets from the deployment secrets file
        """
        # Don't cache secrets if they already exist
        if len(self._secrets) > 0:
            return
        
        # Read from the secrets file and create secrets for each entry
        if os.path.isfile(self._deployment_secrets_path):
            with open(self._deployment_secrets_path, 'r') as f:
                secrets = json.load(f)
                for key, value in secrets.items():
                    self._secrets.append(Secret(key, value))


    def get_secret(self, name:str):
        self.cache_secrets()

        # Return the secret if it has already been cached
        try:
            return self.find_secret(name).value
        except:
            pass

        # Override secret if it exists in local environment variables
        env_var = os.environ.get(name)

        if env_var is not None:
            secret = Secret(name, env_var)
            self._secrets.append(secret)
            return secret.value

        # If secret is not in local environment variables, get it from Cortex
        value = None
        # Get secret
        response = requests.get(
            f'{self._api_url}/secrets/{name}',
                headers=self._headers
        )

        if 'status' not in response:
            value = response.text

        secret = Secret(name, value)
        self._secrets.append(secret)

        return secret.value


    def find_secret(self, name:str):
        # Find secret with name
        for secret in self._secrets:
            if secret.name == name:
                return secret

        raise Exception(f'Secret {name} not found in Cortex.')


    def reset_secrets(self):
        self._secrets = []

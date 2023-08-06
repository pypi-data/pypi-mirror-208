#!/usr/bin/env python3

import requests
import pathlib
import pickle
import json
import yaml
import pandas as pd
import os
from collections import namedtuple


class CortexFile(namedtuple('BaseFile', 'local_dir remote_path size etag last_modified')):
    _loaded_data = None

    @property
    def local_path(self):
        return '{}/{}'.format(self.local_dir, self.name)


    @property
    def name(self):
        # File name with file extension
        return os.path.basename(self.remote_path)


    @property
    def type(self):
        return pathlib.Path(self.remote_path).suffix.replace('.', '')


    @property
    def loaded_data(self):
        return self._loaded_data


    @property
    def isPandasLoadable(self):
        return self.type in ['xls', 'xlsx', 'xlsm', 'xlsb', 'odf', 'ods', 'odt', 'csv']


    def load(self):
        try:
            with open(self.local_path, 'rb') as file:
                if self.type in ['xls', 'xlsx', 'xlsm', 'xlsb', 'odf', 'ods', 'odt']:
                    self._loaded_data = pd.read_excel(file)
                if self.type=='csv':
                    self._loaded_data = pd.read_csv(file)
                if self.type=='parquet':
                    self._loaded_data = pd.read_parquet(file)
                if self.type=='pkl':
                    self._loaded_data = pickle.load(file)
                if self.type=='json':
                    self._loaded_data = json.load(file)
                if self.type=='yml':
                    self._loaded_data = yaml.load(file)
                return self._loaded_data
        except IOError:
            # Throw an exception if there is an unsupported file type
            raise Exception('File {} could not be opened by Cortex File'.format(self.name))
    
    
    def exists(self):
        return os.path.isfile(self.local_path)


class CortexData():
    _api_url = None
    _headers = None
    _local_dir = None
    _files = []


    @property
    def files(self):
        return self._files


    def __init__(self, model_id, api_url, headers, local_dir='data'):
        self._model_id = model_id
        self._api_url = api_url
        self._headers = headers
        self._local_dir = local_dir

        self._files = self._list_remote_files()


    def _list_remote_files(self):
        response = requests.get(
            f'{self._api_url}/models/{self._model_id}/files',
            headers=self._headers
        ).json()

        return [CortexFile(self._local_dir, file['Key'], file['Size'], file['ETag'], file['LastModified'])
                for file in response]


    def download_files(self):
        # Return if there are no files to download
        if len(self._files) == 0:
            return
        
        # Obtain download urls for Cortex data files
        download_urls = requests.get(
            f'{self._api_url}/models/{self._model_id}/files/download',
            headers=self._headers
        )

        download_urls = download_urls.text.replace('[', '').replace(']', '').replace('"', '').split(',')

        for i in range(len(download_urls)):
            response = requests.get(
                download_urls[i]
            )

            file_name = self._files[i].name
            local_path = f'{self._local_dir}/{file_name}'
            
            if not self.find_file(file_name).exists():
                with open(local_path, "wb") as binary_file:
                    # Write bytes to file
                    binary_file.write(response.content)


    def sync_to_cortex(self, file:CortexFile):
        # Syncs an existing file to S3
        if os.path.exists(file.local_path):
            raise Exception('Function not yet implemented!')
        else:
            raise Exception(f'Error syncing file to cortex! File does not exist: {file.local_path}')


    def find_file(self, name:str):
        # Find file with name
        for file in self._files:
            if file.name == name:
                return file
        raise FileNotFoundError(f'File {name} not found in Cortex data.')

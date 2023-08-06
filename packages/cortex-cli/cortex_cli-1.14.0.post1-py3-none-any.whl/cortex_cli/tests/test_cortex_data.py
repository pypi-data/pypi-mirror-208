from cortex_core._cortex_data import CortexData
import os
import pandas as pd


remote_dir = 'demo/data/financial-ethics'
local_dir = 'data'
demo_files = [
    'credit_data.xlsx'
]


def test_init():
    data = CortexData('demo', 'financial-ethics')
    assert data._s3_bucket == 'nh-clients-dev'
    assert data._region == 'us-gov-west-1'
    assert data._object == remote_dir
    assert data._local_dir == local_dir
    assert data._boto3_client != None


def test_list_files():
    data = CortexData('demo', 'financial-ethics')
    cortex_files = data.list_remote_files()
    assert len(cortex_files) == 1

    for file in cortex_files:
        assert file.name in demo_files
        assert file.remote_path == '{}/{}'.format(remote_dir, file.name)
        assert file.local_path == '{}/{}'.format(local_dir, file.name)


def test_download_files():
    data = CortexData('demo', 'financial-ethics')
    cortex_files = data.download_files()
    for file in cortex_files:
        local_path = '{}/{}'.format(local_dir, file.name)

        try:
            assert os.path.exists(local_path)
        finally:
            os.remove(local_path)
            assert not os.path.exists(local_path)


def test_cortex_file_load():
    data = CortexData('demo', 'financial-ethics')
    cortex_files = data.download_files()
    for file in cortex_files:
        local_path = '{}/{}'.format(local_dir, file.name)

        try:
            assert os.path.exists(local_path)
            if file.isPandasLoadable:
                loaded = file.load()
                assert isinstance(loaded, pd.DataFrame)
            else:
                assert True
        finally:
            os.remove(local_path)
            assert not os.path.exists(local_path)

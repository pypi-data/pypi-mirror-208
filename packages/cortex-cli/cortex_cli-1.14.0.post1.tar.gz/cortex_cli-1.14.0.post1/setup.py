from setuptools import find_packages, setup

# Setup custom import schema
# cortex_cli.cli
# cortex_cli.core
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

from cortex_cli import __version__

setup(
    name="cortex_cli",
    version=__version__,
    packages=find_packages(exclude=['tests*']),
    author='Nearly Human',
    author_email='support@nearlyhuman.ai',
    description='Nearly Human Cortex CLI for interacting with model functions.',
    keywords='CLI, API, nearlyhuman, nearly human, cortex',

    python_requires='>=3.8.10',
    # long_description=open('README.txt').read(),
    install_requires=[
        'plumbum',
        'requests',
        'cloudpickle==2.1.0',
        'cookiecutter',
        'conda-pack',
        'mlflow',
        'mlserver',
        'mlserver-mlflow',
        'fairlearn',
        'prophet'
    ],
    package_data={
        'cortex_cli.model_templates': ['*', '*/*', '*/*/*', '*/*/*/*', '*/*/*/*/*', '.*', '*/.*', '*/*/.*', '*/*/*/.*']
    }
)
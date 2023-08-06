# ML Client Template
This repository is the template for creating a new model that can be registered under Cortex.
**NOTE:** The client key should have a dash, and the model name should be uppercase with spaces.

## Prerequisites
- Install [Python 3.8.13](https://github.com/nearlyhuman/development-guide/blob/main/technologies/python.md)

## Running the application
To generate a new project:
1. Install the virtual environment with the requirements.txt
2. Activate the virtual environment
3. Change directories to a root where you want to generate a new Client ML project to
4. Run the cookiecutter command against this github repository
```
venv
pip install -r requirements.txt
activate
cd ../
cookiecutter git@github.com:nearlyhuman/ml-client-template.git
    model_name [Digits Model]:
    description [A model that predicts digits]:
    Select model_type:
    1 - sklearn
    2 - tensorflow
    3 - pyfunc
    Choose from 1, 2, 3 [1]: 3
```
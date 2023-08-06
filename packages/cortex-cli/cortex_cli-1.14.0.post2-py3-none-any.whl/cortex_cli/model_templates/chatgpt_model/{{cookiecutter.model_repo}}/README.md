# {{cookiecutter.model_name}}
{{cookiecutter.description}}

## Prerequisites
- Install [Mamba](https://mamba.readthedocs.io/en/latest/installation.html)

## Build
```
mambda env create -f conda.yml
```

## Running a Model
The application will begin training a model once a commit is pushed to the branch. Model training will not be initiated on the main branch.

You can generate a training using the commands below from the root of this project's directory.
```
mamba activate {{cookiecutter.__model_name}}

# Train locally and produce a model artifact
cortex-cli models run -p ./{{cookiecutter.__model_name}}

# Run the model through the Cortex Pipeline
cortex-cli models run -t -p ./{{cookiecutter.__model_name}}
```

## Modifying the cortex.yml
The structure of the cortex.yml should be
```
model_class: "{{cookiecutter.__model_class}}"
model_path: "src/{{cookiecutter.__model_name}}/{{cookiecutter.__model_name}}.py"
model_repo: "{{cookiecutter.model_repo}}"
base_path: "src/{{cookiecutter.__model_name}}/base.py"
params:
  - gamma: 0.002
pipeline_steps:
  - download_data: "Download data"
  - transform_data: "Transform data"
  - data_contains_pii_ethics_check: "Data PII ethics check"
  - data_balance_ethics_check: "Data balance ethics check"
  - data_bias_ethics_check: "Data bias ethics check"
  - fit: "Fit model"
  - evaluate: "Evaluate model"
  - cleanup_self: "Cleanup model params"
```

The model_class is the class that inherits the Model from base.  The paths are used to inject the module into the Cortex CLI.  And the params are a set of configuration parameters used by the model.
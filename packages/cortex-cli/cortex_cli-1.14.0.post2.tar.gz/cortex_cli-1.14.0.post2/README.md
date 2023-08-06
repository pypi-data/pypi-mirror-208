<p align="center">
    <img src="https://www.nearlyhuman.ai/wp-content/uploads/2022/04/virtual-copy.svg" width="200"/>
</p>

# Nearly Human Cortex CLI
A simple CLI that abstracts the Cortex API.  The application should reflect all of the Cortex routes, and provide a way
to interact with models within an approved client.

## Prerequisites
- Mamba
- Create a github token with repo permissions and set the `GH_TOKEN` environment variable

## Build
```
mamba env create -f ./conda.yml

# Build version of Nearly Human Cortex CLI for release
python -m build
```

## Installing the CLI
```
mamba create -n cortex_cli python=3.10 pip -c conda-forge
mamba activate cortex_cli
pip install cortex-cli
```

## Running the CLI
```
mamba activate cortex_cli
cortex-cli [resource] [action] [parameters ...]
```

Resources include configure, clients, models, pipelines, and inferences.
Actions include get, list, and create.
Parameters are action+resource specific.

### Configure
The profile for the CLI must be configured before use. An API key needs to be generated from the Settings page in the Cortex UI.
```
$ cortex-cli configure
Profile [default]:
API Url [https://api.nearlyhuman.ai]:
API Key []: nh_asdfasdfasdf1341234
```

### Client

#### Get a List of Clients
The registered profile may only associate with one client.  The get command returns information about their client license, profile, and name.
```
$ cortex-cli clients get

[{'_id': '6317eceaeef27d972e86b4ff',
  'clientKey': 'demo',
  'createdDate': '2022-09-07T00:59:22.582Z',
  'description': 'The Cortex Demo Client',
  'experimentId': '1',
  'licensePlan': 'enterprise',
  'name': 'Demo',
  'supportEmail': 'karl.haviland@nearlyhuman.ai',
  'supportPhone': '717-111-2222',
  'updatedDate': '2022-09-07T00:59:22.582Z',
  'website': 'https://www.nearlhuman.ai'}]
```

### Models

#### Initialize a New Model
*NOTE:* Only needed if you want to both create a brand new Cortex ready model and automatically register it with the server.  Start from the workspace directory where the model repo is going to be created locally.
```
$ cortex-cli models init -n my-demo-name
```

#### Register a Model*
*NOTE:* Only needed if you have an existing Cortex Github repository and you want to register it with the server. First, cd to the model's local directory.
```
$ cortex-cli models register -n "My Demo Model" -r my-demo-name
```

#### Get a List of Models
```
$ cortex-cli models list

[{'_id': '632b32731d2faa4ffbade76d',
  'clientKey': 'demo',
  'createdDate': '2022-09-20T15:49:06.882Z',
  'description': 'A model that is initialized through the Cortex CLI.',
  'experimentId': '1',
  'name': 'nmci-chat-2',
  'organization': 'nearlyhuman',
  'repo': 'nmci-chat-2',
  'tags': [],
  'updatedDate': '2022-09-20T15:49:06.882Z'},
 {'_id': '632b43fd1d2faa4ffbade771',
  'clientKey': 'demo',
  'createdDate': '2022-09-21T17:03:57.365Z',
  'description': 'A model that is initialized through the Cortex CLI.',
  'experimentId': '1',
  'name': 'nmci-chat-3',
  'organization': 'nearlyhuman',
  'repo': 'nmci-chat-3',
  'tags': [],
  'updatedDate': '2022-09-21T17:03:57.365Z'},
 ...
 ]
```

#### Get a Model By ID
```
$ cortex-cli models get -i 632b32731d2faa4ffbade76d
{'_id': '632b32731d2faa4ffbade76d',
 'clientKey': 'demo',
 'createdDate': '2022-09-20T15:49:06.882Z',
 'description': 'A model that is initialized through the Cortex CLI.',
 'experimentId': '1',
 'name': 'nmci-chat-2',
 'organization': 'nearlyhuman',
 'repo': 'nmci-chat-2',
 'tags': [],
 'updatedDate': '2022-09-20T15:49:06.882Z'}
```

#### Run a Model's Pipeline
*NOTE:* First, cd to the model's local directory.  Use the `-t` flag to set tracking against the Cortex server.  Otherwise it will simply train locally.
A pipeline is a series of steps that the model performs to transform and validate data, train, and store the model artifact.  This pipeline displays in the
Cortex UI where it can be deployed. The steps that define the pipeline are located in the 
```
$ cortex-cli models run -t
   + Found the model financialchat
   + Did not find existing pipeline for branch main
   + Pipeline Pending with id: 642c68841368f765a05fdb38
                Loading module financialchat from ./src/financialchat/financialchat.py
   + Loaded pipeline steps
   + Download data completed successfully
   + Fit model completed successfully
   + Evaluate model completed successfully
   + Cleanup model params completed successfully
   > Saving pipeline artifacts...
   + Saved the pipeline artifacts to disk: (models/cortex/642c68841368f765a05fdb38)
   > Packing conda environment...
Collecting packages...
Packing environment at '/home/user/mambaforge/envs/financial_chat' to 'models/cortex/642c68841368f765a05fdb38/environment.tar.gz'
[########################################] | 100% Completed | 13.7s
   + Packed conda environment to disk: (models/cortex/642c68841368f765a05fdb38)
   > Uploading pipeline artifacts to Cortex...
   + Uploaded the pipeline artifacts to Cortex
   + Completed Cortex Pipeline Run
```

### Pipelines

#### Get a List of Pipelines

```
$ cortex-cli pipelines list

```

#### Get a Pipeline by ID
```
$ cortex-cli pipelines get -i 134123413412341234

```

#### Deploy a Pipeline
```
$ cortex-cli pipelines deploy -i 134123413412341234

```

#### Undeploy a Pipeline
```
$ cortex-cli pipelines undeploy -i 134123413412341234

```

### Inferences
#### Get a List of Inferences
```
$ cortex-cli inferences list

```

#### Get an Inference by ID
```
$ cortex-cli inferences get -i 134123413412341234

```
"""
The `mlflow_cortex` module provides an API for logging and loading Cortex models. This module
exports Cortex models with the following flavors:

:py:mod:`mlflow.pyfunc`
    Produced for use by generic pyfunc-based deployment tools and batch inference.
"""
# Standard Libraries
import cloudpickle
import pkg_resources
import logging
import os
import importlib
import shutil
import yaml

# External Libraries
import mlflow
from mlflow.pyfunc import PythonModel
from mlflow.models import Model, ModelSignature, ModelInputExample
from mlflow.models.model import MLMODEL_FILE_NAME
from mlflow.utils.file_utils import write_to
from mlflow.models.utils import _save_example
from mlflow.utils.environment import (
    _validate_env_arguments,
    _mlflow_conda_env,
    _process_pip_requirements,
    _process_conda_env,
    _CONDA_ENV_FILE_NAME,
    _REQUIREMENTS_FILE_NAME,
    _CONSTRAINTS_FILE_NAME,
    _PYTHON_ENV_FILE_NAME,
    _PythonEnv,
)
from mlflow.utils.annotations import keyword_only
from mlflow.utils.model_utils import (
    _add_code_from_conf_to_system_path,
    _validate_and_prepare_target_save_path,
)
from mlflow.exceptions import MlflowException
from mlflow.protos.databricks_pb2 import (
    RESOURCE_DOES_NOT_EXIST,
    DIRECTORY_NOT_EMPTY,
)
from mlflow.tracking.artifact_utils import _download_artifact_from_uri
from mlflow.utils.requirements_utils import (
    _check_requirement_satisfied,
    _parse_requirements,
)
from mlflow.utils import (
    PYTHON_VERSION,
    get_major_minor_py_version,
)
from mlflow.utils.file_utils import TempDir, _copy_file_or_tree
from mlflow.pyfunc import PyFuncModel

# Self import
import cortex_cli.core.mlflow.mlflow_cortex as mlflow_cortex


PY_VERSION = 'python_version'


_logger = logging.getLogger(__name__)


FLAVOR_VERSION = 'flavor_version'
PYFUNC_FLAVOR_NAME = 'python_function'
FLAVOR_NAME = 'cortex_python_function'
MAIN = 'loader_module'
CODE = 'code'
DATA = 'data'
ENV = 'env'
CONFIG_KEY_PYTHON_MODEL = 'python_model'
CONFIG_KEY_CLOUDPICKLE_VERSION = 'cloudpickle_version'
SERIALIZATION_FORMAT_PICKLE = 'pickle'
SERIALIZATION_FORMAT_CLOUDPICKLE = 'cloudpickle'
SUPPORTED_SERIALIZATION_FORMATS = [
    SERIALIZATION_FORMAT_PICKLE,
    SERIALIZATION_FORMAT_CLOUDPICKLE,
]

# File name to which custom objects cloudpickle is saved - used during save and load
_CUSTOM_OBJECTS_SAVE_PATH = 'custom_objects.cloudpickle'


@keyword_only
def log_model(
    model,  # cortex_saved_model_dir,
    artifact_path,
    custom_objects=None,
    conda_env=None,
    # signature=None,
    input_example=None,
    registered_model_name=None,
    style=None,
):
    """

    :return:
    """
    return Model.log(
        model=model,  # cortex_saved_model_dir=vega_saved_model_dir,
        artifact_path=artifact_path,
        flavor=mlflow_cortex,
        conda_env=conda_env,
        registered_model_name=registered_model_name,
        # signature=signature,
        input_example=input_example,
        style=style,
    )


@keyword_only
def save_model(
    path,
    code_path=None,
    conda_env=None,
    mlflow_model=None,
    python_model=None,
    artifacts=None,
    custom_objects=None,
    signature: ModelSignature = None,
    input_example: ModelInputExample = None,
    pip_requirements=None,
    extra_pip_requirements=None,
    metadata=None,
    **kwargs,
):
    """Save a cortex model to a local file or a run.


    """
    _validate_env_arguments(conda_env, pip_requirements, extra_pip_requirements)

    mlflow_model = kwargs.pop('model', mlflow_model)
    if len(kwargs) > 0:
        raise TypeError(f'save_model() got unexpected keyword arguments: {kwargs}')
    if code_path is not None:
        if not isinstance(code_path, list):
            raise TypeError('Argument code_path should be a list, not {}'.format(type(code_path)))
    
    _validate_and_prepare_target_save_path(path)
    if mlflow_model is None:
        mlflow_model = Model()
    if signature is not None:
        mlflow_model.signature = signature
    if input_example is not None:
        _save_example(mlflow_model, input_example, path)
    if metadata is not None:
        mlflow_model.metadata = metadata

    # save custom objects if there are custom objects
    if custom_objects is not None and custom_objects != {}:
        _save_keras_custom_objects(path, custom_objects)

    # Custom PyFunc saving logic

    custom_model_config_kwargs = {
        CONFIG_KEY_CLOUDPICKLE_VERSION: cloudpickle.__version__,
        FLAVOR_VERSION: pkg_resources.get_distribution('cortex_cli').version,
    }

    if isinstance(python_model, PythonModel):
        saved_python_model_subpath = 'python_model.pkl'
        with open(os.path.join(path, saved_python_model_subpath), "wb") as out:
            cloudpickle.dump(python_model, out)
        custom_model_config_kwargs[CONFIG_KEY_PYTHON_MODEL] = saved_python_model_subpath
    else:
        raise MlflowException(
            message=(
                '`python_model` must be a subclass of `PythonModel`. Instead, found an'
                ' object of type: {python_model_type}'.format(python_model_type=type(python_model))
            ),
            error_code=INVALID_PARAMETER_VALUE,
        )
    
    saved_code_subpath = None
    if code_path is not None:
        saved_code_subpath = 'code'
        for code in code_path:
            _copy_file_or_tree(src=code, dst=path, dst_dir=saved_code_subpath)
    
    mlflow_model.add_flavor(
        FLAVOR_NAME,
        code=saved_code_subpath,
        env=conda_env,
        loader_module='cortex_cli.core.mlflow.mlflow_cortex',
        python_version=PYTHON_VERSION,
        **custom_model_config_kwargs,
    )
    mlflow_model.add_flavor(
        PYFUNC_FLAVOR_NAME,
        loader_module='cortex_cli.core.mlflow.mlflow_cortex',
        python_version=PYTHON_VERSION,
    )
    mlflow_model.save(os.path.join(path, MLMODEL_FILE_NAME))


def _save_keras_custom_objects(path, custom_objects):
    """
    Save custom objects dictionary to a cloudpickle file so a model can be easily loaded later.

    :param path: An absolute path that points to the data directory within /path/to/model.
    :param custom_objects: Keras ``custom_objects`` is a dictionary mapping
                           names (strings) to custom classes or functions to be considered
                           during deserialization. MLflow saves these custom layers using
                           CloudPickle and restores them automatically when the model is
                           loaded with :py:func:`mlflow.keras.load_model` and
                           :py:func:`mlflow.pyfunc.load_model`.
    """
    import cloudpickle

    custom_objects_path = os.path.join(path, _CUSTOM_OBJECTS_SAVE_PATH)
    with open(custom_objects_path, 'wb') as out_f:
        cloudpickle.dump(custom_objects, out_f)


def _load_pyfunc(path):
    return load_model(path)


def load_model(
    model_uri: str,
    suppress_warnings: bool = False,
    dst_path: str = None,
) -> PyFuncModel:
    """
    Load a model stored in Python function format.

    :param model_uri: The location, in URI format, of the MLflow model. For example:

                      - ``/Users/me/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
                      - ``models:/<model_name>/<model_version>``
                      - ``models:/<model_name>/<stage>``
                      - ``mlflow-artifacts:/path/to/model``

                      For more information about supported URI schemes, see
                      `Referencing Artifacts <https://www.mlflow.org/docs/latest/concepts.html#
                      artifact-locations>`_.
    :param suppress_warnings: If ``True``, non-fatal warning messages associated with the model
                              loading process will be suppressed. If ``False``, these warning
                              messages will be emitted.
    :param dst_path: The local filesystem path to which to download the model artifact.
                     This directory must already exist. If unspecified, a local output
                     path will be created.
    """
    local_path = _download_artifact_from_uri(artifact_uri=model_uri, output_path=dst_path)

    if not suppress_warnings:
        _warn_dependency_requirement_mismatches(local_path)

    model_meta = Model.load(os.path.join(local_path, MLMODEL_FILE_NAME))

    conf = model_meta.flavors.get(FLAVOR_NAME)
    if conf is None:
        raise MlflowException(
            f'Model does not have the "{FLAVOR_NAME}" flavor',
            RESOURCE_DOES_NOT_EXIST,
        )
    model_py_version = conf.get(PY_VERSION)
    if not suppress_warnings:
        _warn_potentially_incompatible_py_version_if_necessary(model_py_version=model_py_version)

    _add_code_from_conf_to_system_path(local_path, conf, code_key=CODE)
    data_path = os.path.join(local_path, conf[DATA]) if (DATA in conf) else local_path

    python_model_subpath = conf[CONFIG_KEY_PYTHON_MODEL]
    python_model = None
    if python_model_subpath is None:
        raise MlflowException('Python model path was not specified in the model configuration')
    with open(os.path.join(local_path, python_model_subpath), 'rb') as f:
        import cloudpickle
        python_model = cloudpickle.load(f)

    # Load custom Keras objects
    custom_objects = None
    custom_objects_path = None
    if os.path.isdir(model_uri):
        if os.path.isfile(os.path.join(model_uri, _CUSTOM_OBJECTS_SAVE_PATH)):
            custom_objects_path = os.path.join(model_uri, _CUSTOM_OBJECTS_SAVE_PATH)
    if custom_objects_path is not None:
        with open(custom_objects_path, "rb") as in_f:
            #pickled_custom_objects = cloudpickle.load(in_f)
            #pickled_custom_objects.update(custom_objects)
            #custom_objects = pickled_custom_objects
            custom_objects = cloudpickle.load(in_f)
    
    if custom_objects is not None:
        keras_utils = importlib.import_module('tensorflow.keras.utils')
        for k, v in custom_objects.items():
            keras_utils.get_custom_objects()['k'] = v
    
    #Download nltk dependencies

    _logger.info('Downloading nltk dependencies...')
    try:
        nltk = importlib.import_module('nltk')
        nltk.data.path.insert(0,'./nltk_data')
        nltk.download('all', download_dir='./nltk_data')
    except:
        pass

    return _CortexModelWrapper(python_model)


def _warn_potentially_incompatible_py_version_if_necessary(model_py_version=None):
    """
    Compares the version of Python that was used to save a given model with the version
    of Python that is currently running. If a major or minor version difference is detected,
    logs an appropriate warning.
    """
    if model_py_version is None:
        _logger.warning(
            "The specified model does not have a specified Python version. It may be"
            " incompatible with the version of Python that is currently running: Python %s",
            PYTHON_VERSION,
        )
    elif get_major_minor_py_version(model_py_version) != get_major_minor_py_version(PYTHON_VERSION):
        _logger.warning(
            "The version of Python that the model was saved in, `Python %s`, differs"
            " from the version of Python that is currently running, `Python %s`,"
            " and may be incompatible",
            model_py_version,
            PYTHON_VERSION,
        )


def _warn_dependency_requirement_mismatches(model_path):
    """
    Inspects the model's dependencies and prints a warning if the current Python environment
    doesn't satisfy them.
    """
    req_file_path = os.path.join(model_path, _REQUIREMENTS_FILE_NAME)
    if not os.path.exists(req_file_path):
        return

    try:
        mismatch_infos = []
        for req in _parse_requirements(req_file_path, is_constraint=False):
            req_line = req.req_str
            mismatch_info = _check_requirement_satisfied(req_line)
            if mismatch_info is not None:
                mismatch_infos.append(str(mismatch_info))

        if len(mismatch_infos) > 0:
            mismatch_str = ' - ' + '\n - '.join(mismatch_infos)
            warning_msg = (
                "Detected one or more mismatches between the model's dependencies and the current "
                f"Python environment:\n{mismatch_str}\n"
                "To fix the mismatches, call `mlflow.pyfunc.get_model_dependencies(model_uri)` "
                "to fetch the model's environment and install dependencies using the resulting "
                "environment file."
            )
            _logger.warning(warning_msg)

    except Exception as e:
        _logger.warning(
            f"Encountered an unexpected error ({repr(e)}) while detecting model dependency "
            "mismatches. Set logging level to DEBUG to see the full traceback."
        )
        _logger.debug("", exc_info=True)


class _CortexModelWrapper:
    """
    Wrapper class that exposes a TensorFlow model for inference via a ``predict`` function such that
    ``predict(data: pandas.DataFrame) -> pandas.DataFrame``. For TensorFlow versions >= 2.0.0.
    """

    def __init__(self, model):
        """
        :param model: A Cortex SavedModel.
        """
        self.model = model

    def predict(self, data):
        try:
            return self.model.predict(data)
        except Exception as e:
            raise Exception(f"Failed to predict with model: {e}")
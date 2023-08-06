import mlflow.pyfunc
from typing import List, Union

from cortex_cli.core.cortex_data import CortexData
from cortex_cli.core.ethics_checks import EthicsManager, EthicsTypeEnum
from cortex_cli.core.drift_checks import DriftManager, DriftTypeEnum
from cortex_cli.core.secrets_manager import SecretsManager


class CortexModel(mlflow.pyfunc.PythonModel):
    """
    Base class for machine learning models. Not used directly.
    """


    def __init__(self, params, model_id, api_url, headers, model_type='cortex'):
        self.params = params
        self.input_example = None
        self.output_example = None
        self.model_type = model_type
        self.cortex_data = CortexData(model_id, api_url, headers)
        self.ethics_manager = None
        self.drift_manager = DriftManager()
        self.secrets_manager = SecretsManager(api_url, headers)

        self.metrics = {}
        self.custom_objects = {}
        self.cleanup_vars = []


    def download_data(self):
        """Downloads data during initial training

            Parameters:
            N/A

            Returns:
            N/A

        """
        # Download files from Cortex
        self.cortex_data.download_files()
        file_names = [file.name for file in self.cortex_data.files]

        # Setup Ethics Manager after all files are downloaded
        self.ethics_manager = EthicsManager(self.cortex_data.files)

        return f'Downloaded Cortex Files: {file_names}'


    def transform_data(self):
        """Transforms data during initial training and deployment

            Parameters:
            N/A

            Returns:
            N/A

        """
        raise NotImplementedError('Method transform_data() must be implemented')


    def load_context(self, context):
        """Internal mlflow function and should not be overridden

            Parameters:
            context: (mlflow context object): Provided automatically during deployment

            Returns:
            N/A

        """
        # Only load_data during training
        if context is None:
            self.download_data()


    def fit(self):
        """Fits model parameters for training

            Parameters:
            N/A

            Returns:
            N/A

        """
        raise NotImplementedError('Method fit() must be implemented')


    def cleanup_self(self):
        """Cleanup self variables after training
           This should include any self variables which should not be pickled

            Parameters:
            N/A

            Returns:
            N/A

        """
        self.secrets_manager.reset_secrets()

        try:
            for s in ['cortex_data', 'ethics_manager'] + self.cleanup_vars:
                if s in self.__dict__:
                    del self.__dict__[s]
        except AttributeError:
            pass

        return 'Successfully cleaned up self variables'


    def predict(self, model_input):
        """Predicts using a TBD model

            Parameters:
            model_input: (pandas.DataFrame, numpy.ndarray, scipy.sparse.(csc.csc_matrix | csr.csr_matrix), List[Any], Dict[str, Any]): Input for prediction

            Returns:
            N/A

        """
        raise NotImplementedError('Method predict() must be implemented')


    def detect_drift(self, inferences):
        """Detects drift between pre-existing inferences tagged with "Testing" on Cortex
        
            Parameters:
            inferences: (List[Tuple(str, numpy.ndarray, numpy.ndarray)]): Inputs for prediction where the first array is the inference output,
            and the second is the inference output

            Returns:
            drift_result: (namedtuple): Output of drift check
        """
        if self.drift_manager is None:
            return 'Drift Manager is not initialized'
        
        # Replace label_column
        drift_check = self.drift_manager.find_drift_check(DriftTypeEnum.INFERENCE)
        drift_check.set_model_instance(self)
        drift_check.set_data_array(inferences)

        drift_result = self.drift_manager.run_by_drift_type(DriftTypeEnum.INFERENCE)
        return drift_result


    def data_balance_ethics_check(self):
        """Checks for imbalance in data

            Parameters:
            N/A

            Returns:
            ethics_result: (namedtuple): Output of ethics check

        """
        if self.ethics_manager is None:
            return 'Ethics Manager is not initialized'
        
        ethics_result = self.ethics_manager.run_by_ethics_type(EthicsTypeEnum.BALANCE)
        return ethics_result


    def data_contains_pii_ethics_check(self):
        """Checks if data contains PII

            Parameters:
            N/A

            Returns:
            ethics_result: (namedtuple): Output of ethics check

        """
        if self.ethics_manager is None:
            return 'Ethics Manager is not initialized'
        
        ethics_result = self.ethics_manager.run_by_ethics_type(EthicsTypeEnum.PII)
        return ethics_result


    def data_bias_ethics_check(self):
        """Checks for bias in data

            Parameters:
            N/A

            Returns:
            ethics_result: (namedtuple): Output of ethics check

        """
        if self.ethics_manager is None:
            return 'Ethics Manager is not initialized'
        
        ethics_result = self.ethics_manager.run_by_ethics_type(EthicsTypeEnum.BALANCE)
        return ethics_result


    def _add_metric(self, metric_name, metric_value):
        """Adds a metric to be automatically saved after training

            Parameters:
            metric_name (str): Name of metric to save
            metric_value (str): Value of metric to save

            Returns:
            str: Success message

        """
        self.metrics[metric_name] = metric_value

        return 'Successfully added metric'
    

    def _add_custom_object(self, object_name, object_value):
        """Adds a custom keras object to the model to be automatically saved and loaded

            Parameters:
            object_name (str): Name of custom object to save
            object_value (str): Value of custom object to save

            Returns:
            str: Success message

        """
        self.custom_objects[object_name] = object_value

        return 'Successfully added custom object'


    def _add_cleanup_var(self, var_name: Union[str, List[str]]):
        """Adds a variable to be cleaned up after training

            Parameters:
            var_name (str / list(str)): Name of variable to clean up

            Returns:
            str: Success message

        """
        if isinstance(var_name, list):
            self.cleanup_vars = self.cleanup_vars + var_name
            return 'Successfully added cleanup variables'
        elif isinstance(var_name, str):
            self.cleanup_vars.append(var_name)
            return 'Successfully added cleanup variable'

        return 'Failed to add cleanup variable(s)'


    def _set_input_output_examples(self, input_example, output_example):
        """Sets input and output examples for the model

            Parameters:
            input_example (pandas.DataFrame, numpy.ndarray, scipy.sparse.(csc.csc_matrix | csr.csr_matrix), List[Any], Dict[str, Any]): An input example for the model
            output_example (pandas.DataFrame, numpy.ndarray, scipy.sparse.(csc.csc_matrix | csr.csr_matrix), List[Any], Dict[str, Any]): An output example for the model

            Returns:
            N/A

        """
        self.input_example = input_example
        self.output_example = output_example


    def __str__(self):
        """Gets the name of the model

            Parameters:
            N/A

            Returns:
            str: Name of the model

        """
        return self.name

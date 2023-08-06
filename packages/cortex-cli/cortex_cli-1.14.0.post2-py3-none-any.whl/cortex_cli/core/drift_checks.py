from enum import Enum
import numpy as np
from collections import namedtuple


DriftType = namedtuple('BaseDriftType', 'drift_type_enum model_instance data_array')
DriftResult = namedtuple('BaseDriftResult', 'drift_type result_str')


class DriftTypeEnum(Enum):
    """
    Enumeration of drift types
    """
    INFERENCE = "Inference"


class DriftCheck():
    """
    Base class for all drift checks
    """
    _drift_type = None
    _model_instance = None
    _data_array = []

    
    @property
    def drift_type(self):
        return self._drift_type

    @property
    def model_instance(self):
        return self._model_instance
    
    @property
    def data_array(self):
        return self._data_array

    def set_model_instance(self, new_val):
        self._model_instance = new_val

    def set_data_array(self, new_val):
        self._data_array = new_val


    def __init__(self, drift_type, data_array):
        self._drift_type = drift_type
        self._data_array = data_array


    def run(self):
        if self._drift_type == DriftTypeEnum.INFERENCE:
            return self.inferences_drift_check(self._model_instance, self._data_array)


    def inferences_drift_check(self, model_instance, data_array):
        total_count = len(data_array)

        if total_count == 0:
            return 'No inferences have been flagged to detect drift.\nConsider tagging inferences to enable automated drift detection.'

        problem_inferences = []
        equal_count = 0
        for inference in data_array:
            prediction = model_instance.predict(None, inference[1])
            if np.array_equal(prediction, inference[2]):
                equal_count += 1
            else:
                # Pull out inference id
                problem_inferences.append(inference[0])
        
        if len(problem_inferences) == 0:
            return f'{equal_count}/{total_count} inferences have passed drift detection.'
        
        return f'{equal_count}/{total_count} inferences have passed drift detection.\nThe inferences which have failed drift detection are: {problem_inferences}'


class DriftManager():
    _drift_types = []
    _drift_checks = []
    _drift_results = []


    def __init__(self):
        self.initialize_drift_types()
        self.initialize_drift_checks()


    def initialize_drift_types(self):
        self._drift_types.append(DriftType(DriftTypeEnum.INFERENCE, None, None))


    def initialize_drift_checks(self):
        for drift_type in self._drift_types:
            # Add individual drift checks
            self._drift_checks.append(DriftCheck(drift_type.drift_type_enum, None))
    

    def run_by_drift_type(self, drift_check_type):
        # Get list of drift checks with type drift_check_type
        drift_checks = [dc for dc in self._drift_checks if dc.drift_type == drift_check_type]

        # Initialize default return values
        result_str = ''

        # Loop through all drift checks with type drift_check_type
        for drift_check in drift_checks:
            # Run drift check
            drift_result = drift_check.run()

            result_str += f'{drift_result}\n'

        # Save drift results
        drift_result = DriftResult(drift_check_type, result_str[:-1])
        self._drift_results.append(drift_result)

        return drift_result


    def find_drift_check(self, drift_check_type):
        for drift_check in self._drift_checks:
            if drift_check_type == drift_check.drift_type:
                return drift_check

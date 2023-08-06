from enum import Enum
import pandas as pd
from scipy.stats import chi2_contingency
from collections import namedtuple


EthicsType = namedtuple('BaseEthicsType', 'ethics_type_enum sensitive_predictor_columns label_column')
EthicsResult = namedtuple('BaseEthicsResult', 'ethics_type result_str risk')


class EthicsRiskEnum(Enum):
    """
    Enumeration of ethics risks
    """
    NO_RISK = "No Risk"
    LOW_RISK='Low Risk'
    MEDIUM_RISK='Medium Risk'
    HIGH_RISK='High Risk'


class EthicsTypeEnum(Enum):
    """
    Enumeration of ethics types
    """
    BALANCE = "Balance"
    BIAS = "Bias"
    PII = "PII"


class EthicsCheck():
    """
    Base class for all ethics checks
    """
    _file = None
    _ethics_type = None
    _sensitive_predictor_columns = None
    _label_column = None


    @property
    def file(self):
        return self._file
    
    @property
    def ethics_type(self):
        return self._ethics_type
    
    @property
    def sensitive_predictor_columns(self):
        return self._sensitive_predictor_columns
    
    @property
    def label_column(self):
        return self._label_column

    def set_sensitive_predictor_columns(self, sensitive_predictor_columns):
        self._sensitive_predictor_columns = sensitive_predictor_columns


    def set_label_column(self, new_val: str):
        self._label_column = new_val


    def __init__(self, file, ethics_type, sensitive_predictor_columns, label_column):
        self._file = file
        self._ethics_type = ethics_type
        self._sensitive_predictor_columns = sensitive_predictor_columns
        self._label_column = label_column


    def run(self):
        file = self._file.loaded_data#self._file.load()
        if file is None:
            return (None, EthicsRiskEnum.NO_RISK)
        if self._ethics_type == EthicsTypeEnum.BALANCE:
            return self.data_balance_ethics_check(file)
        elif self._ethics_type == EthicsTypeEnum.BIAS:
            return self.data_bias_ethics_checks(file, self._sensitive_predictor_columns, self._label_column)
        elif self._ethics_type == EthicsTypeEnum.PII:
            return self.data_contains_pii_ethics_check(file, self._sensitive_predictor_columns)


    def data_balance_ethics_check(self, data, threshold=0.8):
        matched_columns = []

        for col in data.select_dtypes(include=["object", "number", "string"]):
            value_counts = data[col].value_counts(normalize=True)
            if value_counts.max() > threshold:
                matched_columns.append(col)
                # print(f"Column '{col}' has high data imbalance: {value_counts.max()}")
        
        if len(matched_columns) > 0:
            return (f'The dataset contains high data imbalance in the following columns: {matched_columns}', EthicsRiskEnum.MEDIUM_RISK)
        
        return ('The dataset contains balanced data', EthicsRiskEnum.NO_RISK)


    def data_contains_pii_ethics_check(self, data, sensitive_categories):
        """
        Checks if there is pii in the data
        An example for sensitive_categories is: ['name', 'dob', 'gender', 'age', 'address', 'phone', 'email', 'city', 'state', 'zipcode', 'country',
                        'ssn', 'nin', 'passport_number', 'passport_country', 'passport_name', 'cc', 'cc#']
        """
        matched_columns = []

        for column_name in data.columns:
            if column_name.lower() in sensitive_categories:
                matched_columns.append(column_name)
        
        if len(matched_columns) > 0:
            return (f'The dataset contains Personal Identification Information (PII) data in the following columns: {matched_columns}', EthicsRiskEnum.HIGH_RISK)
        
        return ('The dataset does not contain Personal Identification Information (PII) data', EthicsRiskEnum.NO_RISK)


    def data_bias_ethics_checks(self, data, sensitive_categories, y_column):
        """
        Checks if there is bias between sensitive_categories and the predicted y_column
        """
        result = ''
        risk = EthicsRiskEnum.NO_RISK
        if y_column in data.columns:
            for column_name in data.columns:
                if column_name.lower() in sensitive_categories:
                    ethics_check = self.data_bias_ethics_check(data, column_name, y_column)

                    # Set risk level
                    if ethics_check[1] is not EthicsRiskEnum.NO_RISK:
                        risk = ethics_check[1]

                    result += f'{column_name}: {ethics_check[0]}\n'
        return (result[:-1], risk)


    def data_bias_ethics_check(self, data, category, y_column):
        """
        Checks if there is bias between category and the predicted y_column
        """
        text_string = ''
        risk = EthicsRiskEnum.NO_RISK
        
        contingency = pd.crosstab(data[category], data[y_column])
        totals = contingency.sum()
        total_sum = totals.sum()
        totals = totals.apply(lambda x: x/total_sum)
        totals_dict = dict(totals)
        total_list = []
        for k,v in totals_dict.items():
            total_list.append(f'"{k}" {v:.1%} of the time')
        list_str = ' and '.join(total_list)
        total_string = f'The general polutation gets a score of {list_str}.'
        c, p, dof, expected = chi2_contingency(contingency)
        if p <= .05:
            risk = EthicsRiskEnum.HIGH_RISK
            text_string += f'There is a significant bias in your raw data between {y_column} for the {category} subpopulation.\n'
            percentages = pd.crosstab(data[category], data[y_column]).apply(lambda row: row/row.sum(), axis=1).reset_index()
            percentages.set_index(category, drop=True, inplace=True)
            pct_dict = percentages.to_dict('index')
            sub_list = []
            """
            for k, v in pct_dict.items():
                sub_list = []
                for outcome, pct in v.items():
                    sub_list.append(f'"{outcome}" {pct:.1%} of the time')
                text_string += f"\n\t\tThe subcategory: {k} gets a score of: {' and '.join(sub_list)}."
            """
        """
        #making charts
        plt.figure()
        ax = plt.axes()
        sns.heatmap(percentages, annot=True, cmap='Blues')
        ax.set_title(f'{category} percentages by {y_column}')
        plt.savefig(f'data/{category} percentages by {y_column}.png')
        """
        return (text_string, risk)


    """
    TODO: Implement additional functions
    def post_model_checks(data, model, category, X, y_column):
        cat_df = data[category]
        true = data[y_column].copy()
        pred = classifier.predict(X)
        #recoding outcomes to be binary due to a bug in the fair learn code.  
        true[true == '<=50K'] = 0
        true[true == '>50K'] = 1
        pred[pred == '<=50K'] = 0
        pred[pred == '>50K'] = 1
        metrics = {
            'accuracy': accuracy_score,
            'precision': precision_score,
            'recall': recall_score}
        #must make y_true, and y_pred lists for the sklearn type of target param.  It doesn't like the arrays for some weird reason
        metric_frame = MetricFrame(metrics=metrics,
                                y_true=list(true),
                                y_pred=list(pred),
                                sensitive_features=self.cat_df)
        result = metric_frame.by_group.T
        for c in result:
            result[c] = result[c].apply(lambda x: round(x,2))
        post_check = result.to_dict('index')
        #making charts
        plt.figure()
        ax1 = plt.axes()
        ax1.set_title(f'{category} post-model prediction')
        #clrs = ['grey' if (x < max(values)) else 'red' for x in values ]
        metric_frame.by_group.T.plot.bar(ax = ax1, color= ['lightblue','blue','darkblue','royalblue','lightsteelblue'])
        plt.savefig(f'src/financial_chat_ethics/{category} post-model prediction.png')
        return(post_check)
    """


class EthicsManager():
    _ethics_types = []
    _ethics_checks = []
    _ethics_results = []


    def __init__(self, cortex_files):
        self.initialize_ethics_types()
        self.initialize_ethics_checks(cortex_files)


    def initialize_ethics_types(self):
        self._ethics_types.append(EthicsType(EthicsTypeEnum.BALANCE, \
            None, \
            None))
        self._ethics_types.append(EthicsType(EthicsTypeEnum.BIAS, \
            ['gender', 'sex', 'age', 'race'], \
            "label"))
        self._ethics_types.append(EthicsType(EthicsTypeEnum.PII, \
            ['name', 'dob', 'gender', 'age', 'address', 'phone', 'email', 'city', 'state', 'zipcode',
            'country', 'ssn', 'nin', 'passport_number', 'passport_country', 'passport_name', 'cc', 'cc#'], \
            None))


    def initialize_ethics_checks(self, cortex_files):
        # Loop through all Cortex Files
        for file in cortex_files:
            # Check if file can be loaded by Pandas
            if file.isPandasLoadable:
                # Loop through all ethics check types
                for ethics_type in self._ethics_types:
                    # Add individual ethics checks
                    self._ethics_checks.append(EthicsCheck(file, ethics_type.ethics_type_enum,
                     ethics_type.sensitive_predictor_columns, ethics_type.label_column))
    

    def run_by_ethics_type(self, ethics_check_type):
        # Get list of ethics checks with type ethics_check_type
        ethics_checks = [ec for ec in self._ethics_checks if ec.ethics_type == ethics_check_type]

        # Initialize default return values
        result_str = ''
        risk = EthicsRiskEnum.NO_RISK

        # Loop through all ethics checks with type ethics_check_type
        for ethics_check in ethics_checks:
            # Run ethics check
            ethics_result = ethics_check.run()

            if ethics_result[0] is not None:

                # Set risk level
                if ethics_result[1] is not EthicsRiskEnum.NO_RISK:
                    risk = ethics_result[1]
                result_str += f'{ethics_check.file.name}: {ethics_result[0]}\n'
        
        if len(ethics_checks) == 0 or result_str == '':
            result_str = 'No files have been loaded to run ethics check against.'

        # Save ethics results
        ethics_result = EthicsResult(ethics_check_type, result_str[:-1], risk)
        self._ethics_results.append(ethics_result)

        return ethics_result


    def find_ethics_check(self, file_name, ethics_check_type):
        for ethics_check in self._ethics_checks:
            if file_name == ethics_check.file.name and ethics_check_type == ethics_check.ethics_type:
                return ethics_check

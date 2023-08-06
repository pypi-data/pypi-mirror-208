from cortex_core._cortex_data import CortexData, CortexFile
from cortex_core._ethics_checks import EthicsRiskEnum, EthicsTypeEnum, EthicsManager


remote_dir = 'demo/data/financial-ethics'
local_dir = 'data'
demo_files = [
    'credit_data.xlsx'
]

data = CortexData('demo', 'financial-ethics')


def test_init():
    cortex_files = [CortexFile('./tests/fixtures', 'credit_data.xlsx', 0, None, None)]
    ethics_manager = EthicsManager(cortex_files)

    assert len(ethics_manager._ethics_checks) > 0

def test_data_balance_ethics_check():
    cortex_files = [CortexFile('./tests/fixtures', 'credit_data.xlsx', 0, None, None)]
    ethics_manager = EthicsManager(cortex_files)

    ethics_result = ethics_manager.run_by_ethics_type(EthicsTypeEnum.BALANCE)      
    
    assert len(ethics_result.result_str[:-1]) > 10
    assert ethics_result.risk is EthicsRiskEnum.MEDIUM_RISK


def test_data_pii_ethics_check():
    cortex_files = [CortexFile('./tests/fixtures', 'credit_data.xlsx', 0, None, None)]
    ethics_manager = EthicsManager(cortex_files)

    ethics_result = ethics_manager.run_by_ethics_type(EthicsTypeEnum.PII)
    
    assert len(ethics_result.result_str[:-1]) > 10
    assert ethics_result.risk is EthicsRiskEnum.HIGH_RISK


def test_data_bias_ethics_check():
    cortex_files = [CortexFile('./tests/fixtures', 'credit_data.xlsx', 0, None, None)]
    ethics_manager = EthicsManager(cortex_files)

    # TODO - Set label column for data
    bias_check = ethics_manager.find_ethics_check('credit_data.xlsx', EthicsTypeEnum.BIAS)
    bias_check.set_label_column('income')

    ethics_result = ethics_manager.run_by_ethics_type(EthicsTypeEnum.BIAS)
    
    assert len(ethics_result.result_str[:-1]) > 10
    assert ethics_result.risk is EthicsRiskEnum.HIGH_RISK

import os
from io import StringIO
import pytest
import ensuro
import ensuro.wrappers
from ensuro.utils import load_config


@pytest.fixture
def w3provider():
    try:
        from ethproto import w3wrappers
    except Exception:
        raise pytest.skip("web3py not installed")

    contracts_json_path = [os.path.join(os.path.dirname(ensuro.__file__), "contracts")]
    provider = w3wrappers.register_w3_provider(provider_kwargs={"contracts_path": contracts_json_path})

    # To avoid OutOfGas - See https://gitter.im/ethereum/py-evm?at=5b7eb68c4be56c5918854337
    try:
        import eth_tester.backends.pyevm.main as py_evm_main
        py_evm_main.GENESIS_GAS_LIMIT = 10000000
    except ImportError:
        pass

    # w3 = Web3(Web3.EthereumTesterProvider())
    # w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    # w3 = Web3(Web3.HTTPProvider("https://polygon-mumbai.infura.io/v3/f6ee6adc6d4746d6ad002098d1649067"))
    return provider


def test_load_from_blockchain(w3provider):
    policyPoolAddress = "0xaE0eCd63EC5cF813F2457D134b70E90b011052e5"
    policyPool = ensuro.wrappers.PolicyPool.connect(policyPoolAddress)
    assert policyPool.currency.decimals == 18
    etokens = policyPool.etokens
    assert len(etokens) == 1
    risk_modules = policyPool.config.risk_modules
    assert len(risk_modules) == 7
    assert "eUSD1WEEK" in etokens
    assert "0x65335509A96753b1f66c60C59Ac6A85caD273983" in risk_modules
    assert risk_modules["0x65335509A96753b1f66c60C59Ac6A85caD273983"].name == "Test RM"


def xx_test_load_yaml_w3(w3provider):
    YAML_SETUP = """
    risk_modules:
      - name: Roulette
        scr_percentage: 1
        scr_interest_rate: "0.01"
        ensuro_fee: 0
    currency:
        name: USD
        symbol: $
        initial_supply: 6000
        initial_balances:
        - user: LP1
          amount: 3500
        - user: CUST1
          amount: 100
    etokens:
      - name: eUSD1WEEK
        expiration_period: 604800
      - name: eUSD1MONTH
        expiration_period: 2592000
      - name: eUSD1YEAR
        expiration_period: 31536000
    """

    pool = load_config(StringIO(YAML_SETUP), ensuro.wrappers)
    assert "eUSD1WEEK" in pool.etokens
    assert "eUSD1MONTH" in pool.etokens
    assert "eUSD1YEAR" in pool.etokens
    assert "Roulette" in pool.config.risk_modules

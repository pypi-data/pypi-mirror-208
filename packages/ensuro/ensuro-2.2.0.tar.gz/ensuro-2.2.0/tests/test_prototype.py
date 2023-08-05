from io import StringIO
from ensuro.utils import load_config
import ensuro.prototype

__author__ = "Guillermo M. Narvaja"
__copyright__ = "Ensuro"
__license__ = "Apache-2.0"


def test_load_yaml_prototype():
    YAML_SETUP = """
    risk_modules:
      - name: Roulette
        coll_ratio: 1
        sr_roc: "0.01"
        ensuro_pp_fee: 0
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
      - name: eUSD1MONTH
      - name: eUSD1YEAR
    """

    pool = load_config(StringIO(YAML_SETUP), ensuro.prototype)
    assert "eUSD1WEEK" in pool.etokens
    assert "eUSD1MONTH" in pool.etokens
    assert "eUSD1YEAR" in pool.etokens
    assert "Roulette" in pool.risk_modules
